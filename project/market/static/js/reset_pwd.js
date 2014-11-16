$(document).ready(function() {
    $("#forget-pwd-link").click(function(){
        swal({
            title: "Retrieve Your Password",
            text: "Please enter your AndrewID",
            type: "info",
            showCancelButton: true,
            confirmButtonText: 'Ok',
            inputField: true,
            },
            function(str){
                $.get("/send_verification_email", {'username':str}, function(data){
                    if (data != 'success'){
                        swal("An error occured...", "Please enter a valid AndrewID.", "error");
                    } else {
                        swal("Almost there!", "A verification link has been send to you.\nPlease check your email.", "success");
                    }
                });
        });
    });
});