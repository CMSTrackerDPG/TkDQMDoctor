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
                    $.each( data.good, function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="good-runs">' + value + '</span>'
                    });
                    $.each( data.bad, function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="bad-runs">' + value + '</span>'
                    });
                    $.each( data.missing, function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="missing-runs">' +value + '</span>'
                    });
                    $.each( data.prompt_missing, function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="prompt-missing-runs">' +value + '</span>'
                    });
                    $.each( data.changed_good, function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="changed-good-runs">' +value + '</span>'
                    });
                    $.each( data.changed_bad, function( key, value ) {
                        if(newtext !== "")
                            newtext += ", ";
                        newtext += '<span class="changed-bad-runs">' +value + '</span>'
                    });

                    let legend = "";
                    if(data.good.length > 0)
                        legend += '<span class="good-runs">GOOD</span> ';
                    if(data.bad.length > 0)
                        legend += '<span class="bad-runs">BAD</span> ';
                    if(data.missing.length > 0)
                        legend += '<span class="missing-runs">MISSING</span> ';
                    if(data.prompt_missing.length > 0)
                        legend += '<span class="prompt-missing-runs">PROMPT MISSING</span> ';
                    if(data.changed_good.length > 0)
                        legend += '<span class="changed-good-runs"">CHANGED TO GOOD</span> ';
                    if(data.changed_bad.length > 0)
                        legend += '<span class="changed-bad-runs">CHANGED TO BAD</span> ';

                    $("#id-cc-span").html(newtext);
                    $("#id-cc-legend").html("<br/>Legend:" + legend);
                }
            }
        });
    });
});
