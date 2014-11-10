$(document).ready(function() {
    $(".item-photo-list li img").click(function(e){
        $(e.target).closest("div.item-left-col").find("p.item-photo img").attr("src", $(e.target).attr("src"));
    });
});