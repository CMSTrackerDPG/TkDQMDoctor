function disable_date_dropdown_lists() {
    // disables every date dropdown list
    // to simplify url get parameters

    $( "select[name^='date__lte_']" ).each(function(){
        console.log("disabling " + this.name);
        $(this).attr("disabled", "disabled");
    });

    $( "select[name^='date__gte_']" ).each(function(){
        console.log("disabling " + this.name);
        $(this).attr("disabled", "disabled");
    });
}

function simplify_date_filter_parameters(form){
    // converts:
    // ?date__gte_day=2&date__gte_month=7&date__gte_year=2018&date__lte_day=8&date__lte_month=7&date__lte_year=2018
    // to:
    // ?date__gte=2018-7-2&date__lte=2018-7-8

    const gte_day = $("select[name='date__gte_day']").val();
    const gte_month = $("select[name='date__gte_month']").val();
    const gte_year = $("select[name='date__gte_year']").val();

    const lte_day = $("select[name='date__lte_day']").val();
    const lte_month = $("select[name='date__lte_month']").val();
    const lte_year = $("select[name='date__lte_year']").val();

    disable_date_dropdown_lists();

    let date_gte;
    if (gte_day !== "0") {
        date_gte = gte_year + "-" + gte_month + "-" + gte_day;
        console.log("date from: " + date_gte);
        $('<input />').attr('type', 'hidden')
            .attr('name', "date__gte")
            .attr('value', date_gte)
            .appendTo(form);
    }
    let date_lte;
    if (lte_day !== "0") {
        date_lte = lte_year + "-" + lte_month + "-" + lte_day;
        console.log("date until: " + date_lte);
        $('<input />').attr('type', 'hidden')
            .attr('name', "date__lte")
            .attr('value', date_lte)
            .appendTo(form);
    }
}

function disable_empty_filter_fields(form){
    // disables every input field in a form
    // such that it does not appear as a
    // GET parameter in the url

    form.find(":input").filter(function () {
        console.log("disabling " + this.name + ": " + this.value);
        return !this.value || this.value == "0";
    }).attr("disabled", "disabled");
}