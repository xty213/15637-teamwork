$(document).ready(function() {
    $("form.form-rate").submit(function(e){
        $(e.target).addClass("rating");
        swal({
            title: "Rate others",
            text: "Please write down your rate (1, 2, 3, 4, or 5) here:",
            type: "info",
            showCancelButton: true,
            confirmButtonText: 'Ok',
            inputField: true,
            },
            function(rate){
                $("form.rating input[name='rate']").val(rate);
                $.post($("form.rating").attr('action'), {
                        'itemid':$("form.rating input[name='itemid']").val(),
                        'mode':$("form.rating input[name='mode']").val(),
                        'rate':rate,
                        "csrfmiddlewaretoken":$("form.rating input[name='csrfmiddlewaretoken']").val()
                    },
                    function(data){
                        if(data != "success"){
                            swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                        }
                        else {
                            swal("Thanks for your rating!", "Your response is saved.", "success");
                            $("form.rating").after($("form.rating input[name='rate']").val() + "/5");
                            $("form.rating").remove();
                        }
                        $("form.rating").removeClass("rating");
                    }
                );
            }
        );
        return false;
    });
});