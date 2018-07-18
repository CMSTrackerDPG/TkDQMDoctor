/**
 * Pops up the checklist modal when trying to check the checkbox.
 * All checklist items in the modal have to be checked in order to
 * set the main checklist checkbox (e.g. Pixel Checklist)
 */
function popupChecklistModal(checkbox){
    if (checkbox.attr("id").indexOf("item_") === -1) // only on main checkbox
    {
        checkbox.click(function () {
            const checklist = checkbox.attr("id").replace("id_checklist_","");
            $("#modal-"+checklist+"-id").modal();
            return false;
        });
    }
}

/**
 * @param checklist_id: e.g. sistrip
 *
 * Checks if all checklist items have been ticked via html
 * and sets the main checklist checkbox e.g. [x] Pixel Checklist
 *
 * Will be called when the "OK" button in a modal is clicked.
 * It does not submit the form, because it is only used to validate
 * that all checklist items have been ticked.
 */
function validateChecklist(checklist_id) {
    $("#modal-" + checklist_id + "-id").modal('hide');
    $("#id_checklist_" + checklist_id).prop('checked', true);
    return false; // Do not submit the modal form!
}

/**
 * Checks all items in the modal of the specified checklist
 * @param checklist_id: e.g. sistrip
 */
function checkAllItems(checklist_id) {
    $('[id^="id_checklist_"]').each(function() {

        if ($(this).attr("id").indexOf("item_") !== -1 && $(this).attr("id").indexOf(checklist_id) !== -1 ) {
            $(this).prop('checked', true);
        }
    });
}

/**
 * True for visible
 * False for invisible
 */
function setVisibility(dropdownOption, visibility){
    dropdownOption.prop('disabled', !visibility);
}

function getAllCheckedRunTypes(){
    let checkedTypes = [];

    $("input[type='checkbox'][name='runtype']:checked").each(function(){
        checkedTypes.push(this.value);
    });
    return checkedTypes;
}

function getAllCheckedRecoTypes(){
    let checkedTypes = [];

    $("input[type='checkbox'][name='recotype']:checked").each(function(){
        checkedTypes.push(this.value);
    });
    return checkedTypes;
}

function dropdownOptionMatchesCheckedTypes(dropdownOption, runtypes, recotypes){
    const optionText = dropdownOption.text().split(' ').slice(0,2).join(' ').toLowerCase(); //only first 2 words
    const optionRuntype = optionText.split(' ')[1];
    const optionReco = optionText.split(' ')[0];
    // if no checkboxes are ticked then show all
    const matchesRuntype = runtypes.indexOf(optionRuntype) !== -1 || runtypes.length === 0 ;
    const  matchesReco = recotypes.indexOf(optionReco) !== -1 || recotypes.length === 0 ;
    const matches = matchesRuntype && matchesReco;
    return matches
}

/**
 * Filter the options in the Type dropdown menu by checked values
 */
function filterTypeOptionsByCheckboxes(){
    const checked_runtypes = getAllCheckedRunTypes();
    const checked_recotypes = getAllCheckedRecoTypes();


    $('#id_type > option').each(function() {
        let dropdownOption = $(this);
        const typeMatched = dropdownOptionMatchesCheckedTypes(
            dropdownOption, checked_runtypes, checked_recotypes);

        const isSelected =  dropdownOption.is(":selected");  // keep selected option
        setVisibility(dropdownOption, typeMatched || isSelected);
    });
}

function referenceRunMatchesType(dropdownOption, runtype, reco){
    const optionText = dropdownOption.text().toLowerCase().split(' '); //only first 2 words
    const optionRuntype = optionText[2];
    const optionReco = optionText[1];

    const matchesRuntype = runtype === optionRuntype;
    const matchesReco = reco === optionReco;
    const matches = matchesRuntype && matchesReco;
    return matches
}

function updateReferenceRunList(){
    let selectedTypeText = $("#id_type option:selected").text().toLowerCase().split(' ');
    const selectedReco = selectedTypeText[0];
    const selectedRuntype = selectedTypeText[1];
    const selectedBfield = selectedTypeText[2] + " " + selectedTypeText[3];
    const selectedBeamtype = selectedTypeText[4];

    $('#id_reference_run > option').each(function() {
        let dropdownOption = $(this);
        const typeMatched = referenceRunMatchesType(dropdownOption, selectedRuntype, selectedReco);
        const matchTypeIsChecked = $("#id_match_type").is(":checked");
        const isSelected =  dropdownOption.is(":selected");  // keep selected option
        setVisibility(dropdownOption, typeMatched || !matchTypeIsChecked || isSelected);
    });
}
