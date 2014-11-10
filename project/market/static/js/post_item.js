$(document).ready(function() {
        $("#endtime").datetimepicker({
            minuteStep: 1,
            showSeconds: true,
        });

        $("#change-pic-btn").click(function(){
            picNum = parseInt($("#pic-num").val());
            if(picNum < 4){
                picNum += 1;
                $('<input type="file" class="form-control" name="pic' + picNum + '">').insertBefore("#change-pic-btn");
                $("#pic-num").val(picNum);
            }
            if(picNum == 4){
                $("#change-pic-btn").addClass("disabled");
            }
        });

        $(document).on("change", "input[type='radio']", function(e){
            if(e.target.value == "fixed"){
                $("#auction-label").hide();
                $("#auction-end-time").hide();
                $("#endtime").removeAttr("required");
            }
            else if(e.target.value == "auction"){
                $("#auction-label").show();
                $("#auction-end-time").show();
                $("#endtime").attr("required", "required");
            }
        });
});