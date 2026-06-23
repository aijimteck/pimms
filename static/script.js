const config = window.PIMMS_CONFIG || {};

const form = document.querySelector("#intake-form");
const cityBlock = document.querySelector("#city-block");
const districtBlock = document.querySelector("#district-block");
const cityInput = document.querySelector("#city");
const otherBlock = document.querySelector("#other-block");
const otherRequestField = document.querySelector("#other-request");
const mediatorCallout = document.querySelector("#mediator-callout");
const mediatorLink = document.querySelector("#mediator-link");
const mediatorOpenButton = document.querySelector("#mediator-open");
const mediatorDialog = document.querySelector("#mediator-dialog");
const mediatorClose = document.querySelector("#mediator-close");
const mediatorFrame = document.querySelector("#mediator-frame");
const mediatorDialogLink = document.querySelector("#mediator-link-dialog");
const progressFill = document.querySelector("#progress-fill");
const progressText = document.querySelector("#progress-text");
const needsValidationMessage = document.querySelector("#needs-validation-message");
const needsFilterInput = document.querySelector("#needs-filter");
const needsFilterStatus = document.querySelector("#needs-filter-status");
const submissionDialog = document.querySelector("#submission-dialog");
const submissionIdNode = document.querySelector("#submission-id");
const submissionTimestampNode = document.querySelector("#submission-timestamp");
const dialogMessage = document.querySelector("#dialog-message");
const dialogClose = document.querySelector("#dialog-close");
const districtMapToggle = document.querySelector("#district-map-toggle");
const districtMapDialog = document.querySelector("#district-map-dialog");
const districtMapClose = document.querySelector("#district-map-close");
const districtGuidePreviewName = document.querySelector("#district-guide-preview-name");
const districtGuidePreviewText = document.querySelector("#district-guide-preview-text");
const submitButton = form?.querySelector('button[type="submit"]');

const groupCountNodes = Array.from(document.querySelectorAll("[data-group-count]"));
const trackedGroups = groupCountNodes.map((node) => node.dataset.groupCount);
const accordionNodes = Array.from(document.querySelectorAll(".accordion"));
const mediatorHelpLevelKey =
  "j'ai besoin de prendre rendez-vous avec un mediateur social";

let mediatorDialogAutoOpened = false;

function setDisabledState(container, disabled) {
  const fields = container.querySelectorAll("input, select, textarea");
  fields.forEach((field) => {
    field.disabled = disabled;
    if (field.dataset.conditionalRequired === "true") {
      field.required = !disabled;
    }
  });
}

function normalizeText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function updateResidenceVisibility() {
  const residence = form.elements.noisyResident?.value;
  const showCity = residence === "Non";
  const showDistrict = residence === "Oui";

  cityBlock.hidden = !showCity;
  districtBlock.hidden = !showDistrict;

  setDisabledState(cityBlock, !showCity);
  setDisabledState(districtBlock, !showDistrict);

  cityInput.dataset.conditionalRequired = "true";
  cityInput.required = showCity;

  if (!showCity) {
    cityInput.value = "";
  }

  const districtInputs = districtBlock.querySelectorAll('input[name="district"]');
  districtInputs.forEach((input) => {
    input.dataset.conditionalRequired = "true";
    input.required = showDistrict;
    if (!showDistrict) {
      input.checked = false;
    }
  });

  if (!showDistrict) {
    closeDistrictMapDialog();
  }
}

function updateOtherVisibility() {
  const otherChecked = form.querySelector('[data-other-trigger="true"]')?.checked;

  otherBlock.hidden = !otherChecked;
  otherRequestField.dataset.conditionalRequired = "true";
  otherRequestField.required = Boolean(otherChecked);

  if (!otherChecked) {
    otherRequestField.value = "";
  }
}

function setDistrictGuidePreview(name, hint) {
  if (!districtGuidePreviewName || !districtGuidePreviewText) {
    return;
  }

  if (!name || !hint) {
    districtGuidePreviewName.textContent = "Sélectionnez un quartier sur la carte";
    districtGuidePreviewText.textContent =
      "Une recommandation de sélection apparaîtra ici.";
    return;
  }

  districtGuidePreviewName.textContent = name;
  districtGuidePreviewText.textContent = hint;
}

function syncDistrictGuideState() {
  const selectedValue = form.elements.district?.value || "";
  districtMapDialog?.querySelectorAll("[data-district-select]").forEach((node) => {
    node.dataset.active =
      selectedValue && node.dataset.districtSelect === selectedValue ? "true" : "false";
  });
}

function readDistrictMetadata(trigger) {
  if (!trigger) {
    return { name: "", hint: "" };
  }

  return {
    name: trigger.dataset.districtName || trigger.dataset.districtSelect || "",
    hint: trigger.dataset.districtHint || "",
  };
}

function selectDistrictValue(districtValue, trigger) {
  const input = Array.from(form.querySelectorAll('input[name="district"]')).find(
    (field) => field.value === districtValue
  );
  if (!input) {
    return;
  }

  input.checked = true;
  input.dispatchEvent(new Event("change", { bubbles: true }));
  syncDistrictGuideState();

  const metadata = readDistrictMetadata(trigger);
  setDistrictGuidePreview(metadata.name, metadata.hint);
  closeDistrictMapDialog();
  updateProgress();
}

function openDistrictMapDialog() {
  if (!districtMapDialog || typeof districtMapDialog.showModal !== "function") {
    return;
  }

  if (!districtMapDialog.open) {
    districtMapDialog.showModal();
  }

  districtMapToggle?.setAttribute("aria-expanded", "true");
  syncDistrictGuideState();

  const selectedValue = form.elements.district?.value || "";
  const selectedTrigger = selectedValue
    ? districtMapDialog.querySelector(
        `[data-district-select="${selectedValue.replace(/"/g, '\\"')}"]`
      )
    : null;
  const metadata = readDistrictMetadata(selectedTrigger);
  setDistrictGuidePreview(metadata.name, metadata.hint);
}

function closeDistrictMapDialog() {
  if (!districtMapDialog?.open) {
    districtMapToggle?.setAttribute("aria-expanded", "false");
    return;
  }

  districtMapDialog.close();
  districtMapToggle?.setAttribute("aria-expanded", "false");
}

function hasValidMediatorUrl() {
  return Boolean(
    config.mediatorUrl && !String(config.mediatorUrl).includes(".invalid")
  );
}

function syncMediatorTargets() {
  if (!hasValidMediatorUrl()) {
    return;
  }

  mediatorLink.href = config.mediatorUrl;
  mediatorDialogLink.href = config.mediatorUrl;
}

function openMediatorExperience() {
  if (!hasValidMediatorUrl()) {
    return;
  }

  syncMediatorTargets();

  if (mediatorFrame) {
    mediatorFrame.src = config.mediatorUrl;
  }

  if (mediatorDialog && typeof mediatorDialog.showModal === "function") {
    if (!mediatorDialog.open) {
      mediatorDialog.showModal();
    }
    return;
  }

  window.open(config.mediatorUrl, "_blank", "noopener,noreferrer");
}

function closeMediatorDialog() {
  if (!mediatorDialog?.open) {
    return;
  }

  mediatorDialog.close();
}

function updateMediatorCallout() {
  const selectedHelp = form.elements.helpLevel?.value;
  const shouldShow = normalizeText(selectedHelp) === mediatorHelpLevelKey;

  mediatorCallout.hidden = !shouldShow;
  syncMediatorTargets();

  if (!shouldShow) {
    mediatorDialogAutoOpened = false;
    closeMediatorDialog();
    return;
  }

  if (!mediatorDialogAutoOpened && hasValidMediatorUrl()) {
    mediatorDialogAutoOpened = true;
    openMediatorExperience();
  }
}

function updateNeedCounters() {
  trackedGroups.forEach((groupName) => {
    const selector = `input[data-group="${groupName}"]:checked`;
    const count = form.querySelectorAll(selector).length;
    const countNode = document.querySelector(`[data-group-count="${groupName}"]`);
    if (countNode) {
      countNode.textContent = String(count);
    }
  });
}

function validateNeeds(showMessage) {
  const hasSelection = form.querySelectorAll('input[name="needs"]:checked').length > 0;
  needsValidationMessage.hidden = hasSelection || !showMessage;
  return hasSelection;
}

function applyNeedsFilter() {
  const query = normalizeText(needsFilterInput?.value);
  let visibleItems = 0;
  let visibleGroups = 0;

  accordionNodes.forEach((accordion) => {
    const cards = Array.from(accordion.querySelectorAll(".checkbox-grid .choice-card"));
    let groupHasMatch = false;

    cards.forEach((card) => {
      const matches = !query || normalizeText(card.textContent).includes(query);
      card.hidden = !matches;
      if (matches) {
        groupHasMatch = true;
        visibleItems += 1;
      }
    });

    accordion.hidden = !groupHasMatch;
    accordion.open = query ? groupHasMatch : false;

    if (groupHasMatch) {
      visibleGroups += 1;
    }
  });

  if (!needsFilterStatus) {
    return;
  }

  if (!query) {
    needsFilterStatus.textContent =
      "Tapez un mot-clé pour afficher plus vite les démarches utiles.";
    return;
  }

  if (!visibleItems) {
    needsFilterStatus.textContent =
      "Aucune démarche ne correspond à cette recherche.";
    return;
  }

  const itemSuffix = visibleItems > 1 ? "s" : "";
  const groupSuffix = visibleGroups > 1 ? "s" : "";
  needsFilterStatus.textContent =
    `${visibleItems} démarche${itemSuffix} affichée${itemSuffix} dans ` +
    `${visibleGroups} catégorie${groupSuffix}.`;
}

function updateProgress() {
  const checkpoints = [
    () => Boolean(form.elements.lastName.value.trim()),
    () => Boolean(form.elements.firstName.value.trim()),
    () =>
      Boolean(form.elements.birthDay.value) &&
      Boolean(form.elements.birthMonth.value) &&
      Boolean(form.elements.birthYear.value),
    () => Boolean(form.elements.gender.value),
    () => Boolean(form.elements.noisyResident.value),
    () => {
      if (form.elements.noisyResident.value === "Non") {
        return Boolean(form.elements.city.value.trim());
      }
      if (form.elements.noisyResident.value === "Oui") {
        return Boolean(form.elements.district?.value);
      }
      return false;
    },
    () => validateNeeds(false),
    () => Boolean(form.elements.helpLevel.value),
    () => Boolean(form.elements.timeNeeded.value),
  ];

  const completed = checkpoints.filter((checkpoint) => checkpoint()).length;
  const percentage = Math.round((completed / checkpoints.length) * 100);

  progressFill.style.width = `${percentage}%`;
  progressText.textContent = `${percentage} % rempli`;
}

function collectCheckedValues(groupName) {
  return Array.from(
    form.querySelectorAll(`input[data-group="${groupName}"]:checked`)
  ).map((input) => input.value);
}

function buildPayload() {
  const needs = {};
  trackedGroups.forEach((groupName) => {
    const values = collectCheckedValues(groupName);
    if (values.length) {
      needs[groupName] = values;
    }
  });

  return {
    identite: {
      nom: form.elements.lastName.value.trim(),
      prenom: form.elements.firstName.value.trim(),
      dateDeNaissance: {
        jour: form.elements.birthDay.value,
        mois: form.elements.birthMonth.value,
        annee: form.elements.birthYear.value,
      },
      genre: form.elements.gender.value,
    },
    residence: {
      noisyLeGrand: form.elements.noisyResident.value,
      ville: form.elements.city?.value.trim() || "",
      quartier: form.elements.district?.value || "",
    },
    premiereVisite: form.elements.firstVisit?.value || "",
    needs,
    autreDemarche: otherRequestField.value.trim(),
    equipement: {
      impression: form.elements.needPrint?.value || "",
      scan: form.elements.needScan?.value || "",
    },
    aide: {
      niveau: form.elements.helpLevel.value,
      tempsEstime: form.elements.timeNeeded.value,
    },
    informationsFacultatives: {
      rsa: form.elements.rsa?.value || "",
      telephone: form.elements.phone.value.trim(),
    },
  };
}

function showSubmissionSuccess(result) {
  submissionIdNode.textContent = `#${result.submissionId}`;
  submissionTimestampNode.textContent = `Enregistré le ${result.submittedAt}`;
  dialogMessage.textContent =
    "La réponse a bien été enregistrée et ajoutée au tableau de suivi.";

  if (typeof submissionDialog.showModal === "function") {
    submissionDialog.showModal();
  }
}

function setSubmittingState(isSubmitting) {
  if (!submitButton) {
    return;
  }

  submitButton.disabled = isSubmitting;
  submitButton.textContent = isSubmitting
    ? "Enregistrement en cours..."
    : "Enregistrer la réponse";
}

async function submitForm() {
  const needsValid = validateNeeds(true);
  const nativeValid = form.reportValidity();

  if (!nativeValid || !needsValid) {
    return;
  }

  setSubmittingState(true);

  try {
    const response = await fetch(config.submissionEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(buildPayload()),
    });

    const result = await response.json();

    if (!response.ok || !result.ok) {
      const message =
        result?.message ||
        Object.values(result?.errors || {})[0] ||
        "Impossible d'enregistrer la réponse.";
      dialogMessage.textContent = message;
      submissionIdNode.textContent = "Erreur";
      submissionTimestampNode.textContent = "";
      if (typeof submissionDialog.showModal === "function") {
        submissionDialog.showModal();
      }
      return;
    }

    showSubmissionSuccess(result);
    form.reset();
    handleFormReset();
  } catch (error) {
    dialogMessage.textContent =
      "Le formulaire n'a pas pu envoyer les données. Vérifiez que le serveur est bien lancé.";
    submissionIdNode.textContent = "Hors ligne";
    submissionTimestampNode.textContent = "";
    if (typeof submissionDialog.showModal === "function") {
      submissionDialog.showModal();
    }
  } finally {
    setSubmittingState(false);
  }
}

function handleFormReset() {
  window.requestAnimationFrame(() => {
    if (needsFilterInput) {
      needsFilterInput.value = "";
    }
    updateResidenceVisibility();
    updateOtherVisibility();
    mediatorDialogAutoOpened = false;
    closeMediatorDialog();
    closeDistrictMapDialog();
    setDistrictGuidePreview("", "");
    updateMediatorCallout();
    updateNeedCounters();
    applyNeedsFilter();
    syncDistrictGuideState();
    updateProgress();
    needsValidationMessage.hidden = true;
  });
}

function bindEvents() {
  form.addEventListener("change", (event) => {
    if (event.target.name === "noisyResident") {
      updateResidenceVisibility();
    }

    if (
      event.target.matches('[data-other-trigger="true"]') ||
      event.target.name === "needs"
    ) {
      updateOtherVisibility();
      updateNeedCounters();
      validateNeeds(false);
    }

    if (event.target.name === "helpLevel") {
      updateMediatorCallout();
    }

    if (event.target.name === "district") {
      syncDistrictGuideState();
    }

    updateProgress();
  });

  form.addEventListener("input", () => {
    updateProgress();
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    void submitForm();
  });

  form.addEventListener("reset", handleFormReset);

  dialogClose.addEventListener("click", () => {
    submissionDialog.close();
  });

  mediatorOpenButton?.addEventListener("click", () => {
    openMediatorExperience();
  });

  mediatorClose?.addEventListener("click", () => {
    closeMediatorDialog();
  });

  submissionDialog.addEventListener("click", (event) => {
    const rect = submissionDialog.getBoundingClientRect();
    const clickedOutside =
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom;

    if (clickedOutside) {
      submissionDialog.close();
    }
  });

  mediatorDialog?.addEventListener("click", (event) => {
    const rect = mediatorDialog.getBoundingClientRect();
    const clickedOutside =
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom;

    if (clickedOutside) {
      closeMediatorDialog();
    }
  });

  districtMapToggle?.addEventListener("click", () => {
    openDistrictMapDialog();
  });

  districtMapClose?.addEventListener("click", () => {
    closeDistrictMapDialog();
  });

  districtMapDialog?.addEventListener("click", (event) => {
    const rect = districtMapDialog.getBoundingClientRect();
    const clickedOutside =
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom;

    if (clickedOutside) {
      closeDistrictMapDialog();
    }
  });

  districtMapDialog?.addEventListener("mouseover", (event) => {
    const trigger = event.target.closest("[data-district-select]");
    if (!trigger) {
      return;
    }
    const metadata = readDistrictMetadata(trigger);
    setDistrictGuidePreview(metadata.name, metadata.hint);
  });

  districtMapDialog?.addEventListener("focusin", (event) => {
    const trigger = event.target.closest("[data-district-select]");
    if (!trigger) {
      return;
    }
    const metadata = readDistrictMetadata(trigger);
    setDistrictGuidePreview(metadata.name, metadata.hint);
  });

  districtMapDialog?.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-district-select]");
    if (!trigger) {
      return;
    }

    selectDistrictValue(trigger.dataset.districtSelect, trigger);
  });

  districtMapDialog?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }

    const trigger = event.target.closest("[data-district-select]");
    if (!trigger) {
      return;
    }

    event.preventDefault();
    selectDistrictValue(trigger.dataset.districtSelect, trigger);
  });

  districtMapDialog?.addEventListener("close", () => {
    districtMapToggle?.setAttribute("aria-expanded", "false");
  });

  document.querySelector("#city-shortlist")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-city]");
    if (!button) {
      return;
    }
    cityInput.value = button.dataset.city;
    cityInput.focus();
    updateProgress();
  });

  needsFilterInput?.addEventListener("input", () => {
    applyNeedsFilter();
  });
}

bindEvents();
updateResidenceVisibility();
updateOtherVisibility();
updateMediatorCallout();
updateNeedCounters();
applyNeedsFilter();
syncDistrictGuideState();
updateProgress();
