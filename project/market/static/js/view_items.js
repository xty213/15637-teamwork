function formatDate(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes;
    return date.getMonth()+1 + "/" + date.getDate() + "/" + date.getFullYear() + " " + strTime;
}

$(document).ready(function() {
    $(".item-photo-list li img").click(function(e){
        $(e.target).closest("div.item-left-col").find("p.item-photo img").attr("src", $(e.target).attr("src"));
    });

    $("#form-fixed-price").submit(function(e){
        swal({
            title: "Provide more details",
            text: "Please write about the trading place, trading time, and other concerns. This messages will be sent to the seller via email.",
            type: "info",
            showCancelButton: true,
            confirmButtonText: 'Ok',
            inputField: true,
            },
            function(msg){
                $.post($("#form-fixed-price").attr('action'), {
                            'itemid':$("#form-fixed-price input[name='itemid']").val(),
                            "msg":msg,
                            "csrfmiddlewaretoken":$("#form-fixed-price input[name='csrfmiddlewaretoken']").val()
                            },
                        function(data){
                            if(data != "success"){
                                swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                            }
                            else{
                                swal("It's a deal!", "Congratulations, this item is yours now!\nThe seller will got an email about the deal.", "success");
                                $("#heading-btn-group").hide();
                                $("<p class='pull-right text-danger'></p>").text("Sold at " + formatDate(new Date())).insertBefore("#heading-btn-group");
                            }
                        });
            }
        );
        return false;
    });
});