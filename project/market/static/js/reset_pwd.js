$(document).ready(function() {
    $("#forget-pwd-link").click(function(){
        alertify.prompt("Retrieve Your Password", function (e, str) {
            if (e) {
                $.get("/send_verification_email", {'username':str}, function(data){
                    if (data != 'success'){
                        alertify.alert("An error occured. Please check your AndrewID.");
                    } else {
                        alertify.alert("A verification link has been send to you. Please check your email.");
                    }
                });
            }
        }, "Please enter your AndrewID");
    });
});