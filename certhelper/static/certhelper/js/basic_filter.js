$(document).ready(function () {
    const request_get_params= window.location.search.substr(1);

    if(request_get_params.indexOf("runs") != -1 ||
        request_get_params.indexOf("type") != -1 || request_get_params.indexOf("category") != -1)
        $("#more").collapse('show');

    if(request_get_params.indexOf("date_range") != -1){
        $('#date_day').css('display', 'none');
        $('#date_range').css('display', 'inline');
    }

    if ($("#id_subcategory").val() == "") {
        $("#id_subcategory").hide()
        $("#id_subsubcategory").hide()
    }

    $("#id_category").change(function () {
        var category_id = $(this).val();  // get the selected category_id from the dropdown menu

        $.ajax({
            url: "{% url 'certhelper:ajax_load_subcategories' %}",  // pass categoryId to load_subcategories view
            data: {
                'categoryid': category_id  // add the category_id to the GET parameters
            },
            success: function (data) {  // date is the return of the load_subcategories view function
                $("#id_subcategory").html(data);  // replace dropdown options with with the data from load_subcategories view
            }
        });
        $('#id_subcategory').val('').trigger('change');  //trigger a change in subcategory to also update subsubcategories

        if (category_id != "") {
            $("#id_subcategory").show()
        } else {
            $("#id_subcategory").hide()
        }
    });

    $("#id_subcategory").change(function () {
        var subcategory_id = $(this).val();

        $.ajax({
            url: "{% url 'certhelper:ajax_load_subsubcategories' %}",
            data: {
                'subcategoryid': subcategory_id
            },
            success: function (data) {
                $("#id_subsubcategory").html(data);
            }
        });

        if (subcategory_id != "") {
            $("#id_subsubcategory").show()
        } else {
            $("#id_subsubcategory").hide()
        }
    });

    $("#show-filter-btn").click(function () {
        $("#more").collapse('toggle');
    });

    $("#clear-filters").click(function () {
        $('#id_date_range_0').val("");
        $('#id_date_range_1').val("");
        $('#id_date_day').val(0);
        $('#id_date_month').val(0);
        $('#id_date_year').val(0);
        $('#id_category').val("");
        $('#id_subcategory').val("");
        $('#id_subsubcategory').val("");
        $('#id_type').val("");
        $('#id_runs_0').val("");
        $('#id_runs_1').val("");
    });

    $("#radio_day").change(function () {
        $('#date_day').css('display', 'inline');
        $('#date_range').css('display', 'none');

        $('#id_date_range_0').val("");
        $('#id_date_range_1').val("");
    });


    $("#radio_range").change(function () {
        $('#date_day').css('display', 'none');
        $('#date_range').css('display', 'inline');

        document.getElementById("id_date_day").value = 0;
        document.getElementById("id_date_month").value = 0;
        document.getElementById("id_date_year").value = 0;
    });

    $("#more").on('show.bs.collapse', function () {
        $("#show-filter-btn").html('<span class=\"glyphicon glyphicon-menu-up\"></span> Show Less');
        $("#filter-button-bottom").css('display', 'inline');
        $("#filter-button-top").css('display', 'none');
    });
    $("#more").on('hide.bs.collapse', function () {
        $("#show-filter-btn").html('<span class=\"glyphicon glyphicon-menu-down\"></span> Show More');
        $("#filter-button-bottom").css('display', 'none');
        $("#filter-button-top").css('display', 'inline');
    });
});
