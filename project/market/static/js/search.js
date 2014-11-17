$(document).ready(function() {
    $("#header-search ul.dropdown-menu li a").click(function(e){
        var a = e.target;
        $("#selected_category").text($(a).text());
        $("#header-search input[name='category']").val($(a).attr("value"));
    });
});