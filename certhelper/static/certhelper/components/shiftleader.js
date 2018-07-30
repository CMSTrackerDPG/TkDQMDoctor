$(document).ready(function () {

    $(document).ready(function(){
        $('[data-toggle="tooltip"]').tooltip();
    });

    $("#id-cc-input").keyup(function () {
        let text = $("#id-cc-input").val();

        $.ajax({
            url: '/ajax/validate-cc-list/',
            data: {
                'text': text
            },
            dataType: 'json',
            success: function (data) {
                if (data) {
                    let newtext = "";
                    $.each( data.good.sort(function(a, b){return a-b}), function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="good-runs">' +value + '</span>'
                    });
                    $.each( data.bad.sort(function(a, b){return a-b}), function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="bad-runs">' + value + '</span>'
                    });
                    $.each( data.missing.sort(function(a, b){return a-b}), function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="missing-runs">' +value + '</span>'
                    });
                    $.each( data.different_flags.sort(function(a, b){return a-b}), function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="different-flags">' +value + '</span>'
                    });

                    let legend = "";
                    if(data.good.length > 0)
                        legend += '<span class="good-runs""> GOOD </span>';
                    if(data.bad.length > 0)
                        legend += '<span class="bad-runs"> BAD </span>';
                    if(data.missing.length > 0)
                        legend += '<span class="missing-runs"> MISSING </span>';
                    if(data.different_flags.length > 0)
                        legend += '<span class="different-flags"> DIFFERENT Flags</span>';

                    $("#id-cc-span").html(newtext);
                    $("#id-cc-legend").html("<br/>Legend:" + legend);
                }
            }
        });
    });
});
