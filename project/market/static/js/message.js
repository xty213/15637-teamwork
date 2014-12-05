
$(document).ready(function(){
    $("#new-msg-form").submit(function(e){
        $.post($("#new-msg-form").attr('action'), {
                    'username':$("#new-msg-form input[name='username']").val(),
                    'title':$("#new-msg-form input[name='title']").val(),
                    'content':$("#new-msg-form textarea[name='content']").val(),
                    "csrfmiddlewaretoken":$("#new-msg-form input[name='csrfmiddlewaretoken']").val()
                    },
                function(data){
                    if(data.indexOf("success") != 0){
                        swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                    }
                    else{
                        $("#new-msg-modal").modal("hide");
                        showNewMsgInOutbox(data.split(" ")[1],
                                           $("#new-msg-form input[name='username']").val(),
                                           $("#new-msg-form input[name='title']").val());
                        swal({title: "The message is sent!", type: "success"});
                    }
                });
        return false;
    });
});

function showNewMsgModal(){
    $("#new-msg-form input[name='username']").val("");
    $("#new-msg-form input[name='title']").val("");
    $("#new-msg-form textarea[name='content']").val("");
    $("#new-msg-modal").modal("show");
}

function showNewMsgInOutbox(id, receiver, title){
    $("<tr><td><a href='javascript:void(0);' onclick='showMsg(" + id + ", false)'>" + title + "</a></td><td>" + receiver + "</td><td>" + formatDate(new Date()) + "</td><td><a href='javascript:void(0);' onclick='delMsg(" + id + ")'>Delete</a></td></tr>").insertAfter("#outbox-panel table tbody tr:first-child");
}

function showMsg(id, showReplyBtn){
    $.get("/show_message/"+id, function(data){
        $("#show-msg-modal-label").text(data.title);
        $("#show-msg-form input[name='receiver']").val(data.receiver);
        $("#show-msg-form input[name='sender']").val(data.sender);
        $("#show-msg-form textarea[name='content']").val(data.content);

        if (showReplyBtn) {
            $("#reply-msg-btn").show();
        } else {
            $("#reply-msg-btn").hide();
        }
        $("#show-msg-modal").modal("show");
    });
}

function delMsg(id){
    $.get("/delete_message/"+id, function(data){
        if(data != "success"){
            swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
        } else {
            swal({title: "The message is deleted!", type: "success"});
            $("#table-row-" + id).remove();
        }
    });
}

function prepReplyMsgBox(){
    $("#new-msg-form input[name='username']").val($("#show-msg-form input[name='sender']").val());
    $("#new-msg-form input[name='title']").val("RE:" + $("#show-msg-modal-label").text().substring(0, 30));
    $("#show-msg-modal").modal("hide");
    $("#new-msg-modal").modal("show");
}

function formatDate(date) {
    var year = date.getFullYear();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var month = date.getMonth()+1;
    var date = date.getDate();

    hours = hours < 10 ? '0'+hours : hours;
    minutes = minutes < 10 ? '0'+minutes : minutes;
    month = month < 10 ? '0'+month : month;
    date = date < 10 ? '0'+date : date;

    return month + "/" + date + "/" + year + " " + hours + ':' + minutes;
}