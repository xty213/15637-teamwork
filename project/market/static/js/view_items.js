function formatDate(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var month = date.getMonth()+1;
    var date = date.getDate();
    var year = date.getFullYear();

    hours = hours < 10 ? '0'+hours : hours;
    minutes = minutes < 10 ? '0'+minutes : minutes;
    month = month < 10 ? '0'+month : month;
    date = date < 10 ? '0'+date : date;

    return month + "/" + date + "/" + year + " " + hours + ':' + minutes;
}

function number_format(number, decimals, dec_point, thousands_sep) {
  number = (number + '')
    .replace(/[^0-9+\-Ee.]/g, '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
      var k = Math.pow(10, prec);
      return '' + (Math.round(n * k) / k)
        .toFixed(prec);
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n))
    .split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '')
    .length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1)
      .join('0');
  }
  return s.join(dec);
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

    $("#form-place-bid").submit(function(e){
        swal({
            title: "Give your bid",
            text: "Please write down your bid.\nIt should higher than the current price for at least $0.5",
            type: "info",
            showCancelButton: true,
            confirmButtonText: 'Place Bid',
            inputField: true,
            },
            function(price){
                $("#form-place-bid input[name='bid_price']").val(price);
                $.post($("#form-place-bid").attr('action'), {
                            'itemid':$("#form-place-bid input[name='itemid']").val(),
                            "price":price,
                            "csrfmiddlewaretoken":$("#form-place-bid input[name='csrfmiddlewaretoken']").val()
                            },
                        function(data){
                            if(data != "success"){
                                swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                            }
                            else{
                                swal("Congratulations!", "The bid is placed successfully.", "success");
                                var bidder = $("#form-place-bid input[name='curr_user']").val();
                                var bid_price = "$" + number_format($("#form-place-bid input[name='bid_price']").val(), 2, ".", "");
                                $("#curr_bid").text(bid_price);
                                $("#curr_bidder").text(bidder);
                                if ($("div.item-bidding-hist table").length == 0){
                                    $("<table class='table table-striped table-condensed'><tbody><tr><th>Bidder</th><th>Bid Amount</th><th>Bid Time</th></tr></tbody></table>").insertAfter("div.item-bidding-hist p");
                                    $("div.item-bidding-hist p").remove();
                                }
                                $("<tr><td>" + bidder + "</td><td>" + bid_price +"</td><td>" + formatDate(new Date()) +"</td></tr>").insertAfter("div.item-bidding-hist table tr:first-child");
                            }
                        });
            }
        );
        return false;
    });

    $("#form-ask-question").submit(function(e){
        swal({
            title: "Ask a question",
            text: "Please write down your question here:",
            type: "info",
            showCancelButton: true,
            confirmButtonText: 'Ok',
            inputField: true,
            },
            function(question){
                $("#form-ask-question input[name='question']").val(question);
                $.post($("#form-ask-question").attr('action'), {
                            'itemid':$("#form-ask-question input[name='itemid']").val(),
                            "question":question,
                            "csrfmiddlewaretoken":$("#form-ask-question input[name='csrfmiddlewaretoken']").val()
                            },
                        function(data){
                            if(data != "success"){
                                swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                            }
                            else{
                                swal("Good question!", "Wait for a sec, the answer is on the way.", "success");
                                if ($("div.item-qa p").length == 0){
                                    $("<li><span class='item-qa-sign'>Q:</span> <span>" + $("#form-ask-question input[name='question']").val() + "</span></li>").appendTo("div.item-qa ul");
                                }
                                else{
                                    $("div.item-qa p").remove();
                                    $("<ul><li><span class='item-qa-sign'>Q:</span> <span>" + $("#form-ask-question input[name='question']").val() + "</span></li></ul>").appendTo("div.item-qa");
                                }
                            }
                        });
            }
        );
        return false;
    });

    $("form.form-answer").submit(function(e){
        $(e.target).addClass("answering");
        swal({
            title: "Answer a question",
            text: "Please write down your answer here:",
            type: "info",
            showCancelButton: true,
            confirmButtonText: 'Ok',
            inputField: true,
            },
            function(ans){
                $("form.answering input[name='answer']").val(ans);
                $.post($("form.answering").attr('action'), {
                        'questionid':$("form.answering input[name='questionid']").val(),
                        'answer':ans,
                        "csrfmiddlewaretoken":$("form.answering input[name='csrfmiddlewaretoken']").val()
                    },
                    function(data){
                        if(data != "success"){
                            swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                        }
                        else {
                            swal("Thanks for your answer!", "Your answer is saved.", "success");
                            $("form.answering").after("<span class='item-qa-sign'>A:</span> <span>" + $("form.answering input[name='answer']").val() + "</span>");
                            $("form.answering").remove();
                        }
                        $("form.answering").removeClass("answering");
                    }
                );
            }
        );
        return false;
    });

    $("#form-off-the-shelf").submit(function(e){
        $.post($("#form-off-the-shelf").attr('action'), {
                    'itemid':$("#form-off-the-shelf input[name='itemid']").val(),
                    "csrfmiddlewaretoken":$("#form-off-the-shelf input[name='csrfmiddlewaretoken']").val()
                    },
                function(data){
                    if(data != "success"){
                        swal("Opps! An error?", "Something wrong with your request.\nThe error message is \"" + data + "\"\nPlease try again later.", "error");
                    }
                    else{
                        swal({title: "Success!", text: "The item is off the shelf now.\nRedirecting in 3 seconds...", type: "success", timer: 3000 });
                        setTimeout(function(){ window.location="/"; }, 3000);
                    }
                });
        return false;
    });
});