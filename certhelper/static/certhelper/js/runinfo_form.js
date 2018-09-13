/***************
 * GETTER
 *
 * get functions
 **************/

function get_selected_type(){
    return $("#id_type").find(":selected")
}

function get_selected_reference_run(){
    return $("#id_reference_run option:selected")
}

function get_selected_runtype(){
    return get_selected_type().text().split(' ')[1]
}

function get_selected_reco(){
    return get_selected_type().text().split(' ')[0]
}

function get_selected_reference_run_number(){
    return $("#id_reference_run option:selected").text().split(' ')[0];
}

function get_run_number(){
    return $('#id_run_number').val();
}

function get_int_luminosity(){
    return $('#id_int_luminosity').val();
}

function get_number_of_ls(){
    return $('#id_number_of_ls').val();
}

function get_pixel(){
    return  $("#id_tracking").find(":selected").val()
}

function get_sistrip(){
    return  $("#id_tracking").find(":selected").val()
}

function get_tracking(){
    return  $("#id_tracking").find(":selected").val()
}


function get_selected_component_text(component){
    return  $("#id_" + component).find(":selected").text()
}

function get_selected_component_lowstat(component){
    return  $("#id_" + component + "_lowstat").is(":checked")
}

function get_counterpart_type(){
    const reco = get_selected_reco();
    if(reco === "Prompt") return "Express";
    if(reco === "Express") return "Prompt";
    return reco;
}

/********************************************************************
 * VALIDATION
 *
 * Functions for client-side and asynchronous RunInfo form validation
 *******************************************************************/

function validate_type() {
    clear_validation("type");
    validate_form_field_asynchronously("runtype");
    validate_form_field_asynchronously("bfield");
    validate_form_field_asynchronously("beamtype");
}

function validate_run_number(){
    const run_number_text = get_run_number();
    const reference_run_number = get_selected_reference_run_number();
    if(run_number_text !== ""){
        if(run_number_text < 300000){
            display_validation_error("run_number", "Run number is too low");
        } else if(run_number_text > 999999){
            display_validation_error("run_number", "Run number is too high");
        } else if(Math.abs(reference_run_number - run_number_text) > 6000) {
            const warning_text = "Run number seems odd. Please check";
            display_validation_warning("run_number", warning_text);
        } else {
            display_validation_success("run_number", "");
        }
    }
}

function validate_int_luminosity(){
    const int_lumi = get_int_luminosity();
    if(int_lumi){
        let runtype = get_selected_runtype();
        if(runtype === "Cosmics" && int_lumi > 0){
            const warning_text = "You certify a cosmics run. Are you sure about this value?";
            display_validation_warning("int_luminosity", warning_text);
        } else {
            display_validation_success("int_luminosity", "");
            validate_form_field_asynchronously("int_luminosity");
        }
    }
}

function validate_number_of_ls() {
    if(get_number_of_ls()){
        clear_validation("number_of_ls");
        validate_form_field_asynchronously("number_of_ls");
    }
}

function validate_pixel(){
    if(get_pixel()){
        clear_validation("pixel");
        validate_form_field_asynchronously("pixel");
    }
}

function validate_sistrip(){
    if(get_sistrip()){
        clear_validation("sistrip");
        validate_form_field_asynchronously("sistrip");
    }
}

function validate_tracking(){
    if(get_tracking()){
        const pixel = get_selected_component_text("pixel");
        const sistrip = get_selected_component_text("sistrip");
        const tracking = get_selected_component_text("tracking");
        const runtype = get_selected_runtype();

        let error_text = "";
        if(sistrip === "Bad" && tracking === "Good"){
            error_text = "Tracking cant be good if SiStrip is Bad.";
        } else if(sistrip === "Excluded" && tracking === "Good"){
            error_text = "Tracking cant be good if SiStrip is Excluded.";
        } else if (runtype === "Collisions" && pixel === "Bad" && tracking === "Good"){
            error_text = "In Collisions Tracking cant be good if Pixel is Bad.";
        } else if (runtype === "Collisions" && pixel === "Excluded" && tracking === "Good"){
            error_text = "In Collisions Tracking cant be good if Pixel is Excluded.";
        } else {
            clear_validation("tracking");
            validate_form_field_asynchronously("tracking");
        }

        if(error_text)
            display_validation_error("tracking", error_text);
    }
}

/**
 * Special treatment for Internet Explorer
 * https://soledadpenades.com/posts/2007/arrayindexof-in-internet-explorer/
 */
if(!Array.indexOf){
    Array.prototype.indexOf = function(obj){
        for(var i=0; i<this.length; i++){
            if(this[i]==obj){
                return i;
            }
        }
        return -1;
    }
}

function generate_integrity_error_message(field_name, errors)
{
    let error_message = "";
    const counterpart = get_counterpart_type();
    if(field_name.indexOf("pixel") !== -1 || field_name.indexOf("sistrip") !== -1 || field_name.indexOf("tracking") !== -1)
    {
        if (field_name in errors || field_name + "_lowstat" in errors) // pixel, sistrip, tracking
        {
            const component = errors[field_name];
            const component_lowstat = errors[field_name + "_lowstat"];

            if (component)
                error_message = component + " ";
            if (component_lowstat !== undefined){
                error_message += (component_lowstat) ? "Lowstat" : "NOT Lowstat";
            }
        }
    }
    else if(["runtype", "bfield", "beamtype"].indexOf(field_name) !== -1) // type
    {
        // TODO this will be called up to 3 times. Try reducing it to 1.
        // TODO Maybe use "type" instead of the 3 type attributes
        if ("runtype" in errors)
            error_message += errors["runtype"] + " ";
        if ("bfield" in errors)
            error_message += errors["bfield"] + " ";
        if ("beamtype" in errors)
            error_message += errors["beamtype"] + " ";
    }
    else // number_of_ls, int_luminosity
    {
        const expected_field_value = errors[field_name];
        error_message = expected_field_value ? expected_field_value : "";
    }

    if(error_message !== undefined)  // At least one error
        return "" + counterpart + " was certified as: " + error_message;
    return "";  // No errors, should probably not have happened
}

function display_integrity_error(field_name, errors){
    const error_message = generate_integrity_error_message(field_name, errors);
    if(["runtype", "bfield", "beamtype"].indexOf(field_name) !== -1)
        field_name = "type";
    display_validation_warning(field_name, error_message)
}

function clear_validation(field_name){
    // TODO try const instead of let
    // TODO write function get_form_group(field_name)
    let form_group = $("#id_" + field_name).closest(".form-group");
    form_group.removeClass("has-success");
    form_group.removeClass("has-warning");
    form_group.removeClass("has-error");
    form_group.find(".help-block").text("");
    // TODO consider returning form_group
}

function set_help_block_text_and_class(field_name, error_text, css_class){
    // TODO use clear_validation
    let form_group = $("#id_" + field_name).closest(".form-group");
    let help_block = form_group.find(".help-block");
    form_group.removeClass("has-success");
    form_group.removeClass("has-warning");
    form_group.removeClass("has-error");
    form_group.addClass(css_class);
    help_block.text(error_text);
}

function display_validation_error(field_name, error_text){
    set_help_block_text_and_class(field_name, error_text, "has-error")
}

function display_validation_warning(field_name, error_text){
    set_help_block_text_and_class(field_name, error_text, "has-warning")
}

function display_validation_success(field_name, error_text){
    set_help_block_text_and_class(field_name, error_text, "has-success")
}

function get_form_data(){
    const type_id = get_selected_type().val();
    const reference_run_id = get_selected_reference_run().val();
    const run_number = get_run_number();
    const int_luminosity = get_int_luminosity();
    const number_of_ls = get_number_of_ls();
    const pixel = get_selected_component_text("pixel");
    const sistrip = get_selected_component_text("sistrip");
    const tracking = get_selected_component_text("tracking");
    const pixel_lowstat = get_selected_component_lowstat("pixel");
    const sistrip_lowstat = get_selected_component_lowstat("sistrip");
    const tracking_lowstat = get_selected_component_lowstat("tracking");

    return {
        'type': type_id,
        'reference_run': reference_run_id,
        'run_number': run_number,
        'int_luminosity': int_luminosity,
        'number_of_ls': number_of_ls,
        'pixel': pixel,
        'sistrip': sistrip,
        'tracking': tracking,
        'pixel_lowstat': pixel_lowstat,
        'sistrip_lowstat': sistrip_lowstat,
        'tracking_lowstat': tracking_lowstat,
    }
}

function validate_form_field_asynchronously(field_name) {
    const form_data = get_form_data();
    if (form_data.run_number && form_data.type) {
        $.ajax({
            url: '/ajax/check_integrity_of_run/',
            data: form_data,
            dataType: 'json',
            success: function (errors) {
                if (Object.keys(errors).length !== 0) { // at least 1 error
                    if (field_name in errors || field_name + "_lowstat" in errors)
                        display_integrity_error(field_name, errors);
                }
            }
        });
    }
}

function validate_form(){
    validate_type();
    validate_run_number();
    validate_number_of_ls();
    validate_int_luminosity();
    validate_pixel();
    validate_sistrip();
    validate_tracking();
}

function remove_css_class_from_successfully_validated_fields(){
    $(".has-success").removeClass("has-success");
}

/****************
 * MISC
 *
 * miscellaneous functions
 ***************/

function disable_lowstat_for_excluded_components(component_id){
    const selector = "#" + component_id + " option:checked";
    const option = $(selector).val();
    const lowstat_selector = "#" + component_id + "_lowstat";
    if(option === "Excluded"){
        $(lowstat_selector).prop('disabled', true);
    } else {
        $(lowstat_selector).prop('disabled', false);
    }
}

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
    return matchesRuntype && matchesReco;
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

    const selectedReco = get_selected_reco().toLowerCase();
    const selectedRuntype = get_selected_runtype().toLowerCase();

    $('#id_reference_run > option').each(function() {
        let dropdownOption = $(this);
        const typeMatched = referenceRunMatchesType(dropdownOption, selectedRuntype, selectedReco);
        const matchTypeIsChecked = $("#id_match_type").is(":checked");
        const isSelected =  dropdownOption.is(":selected");  // keep selected option
        setVisibility(dropdownOption, typeMatched || !matchTypeIsChecked || isSelected);
    });
}

function round_int_luminosity(){
    let int_luminosity = $("#id_int_luminosity");
    if(int_luminosity.val()){
        const rounded = parseFloat(int_luminosity.val()).toFixed(1);
        int_luminosity.val(rounded);
    }
}
