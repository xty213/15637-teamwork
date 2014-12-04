var displaying = "#account-info-tab";

function showTab(tabStr){
    if (tabStr == displaying) {
        return;
    } else {
        $(displaying).fadeOut(200, function(){
            $(tabStr).fadeIn(200);
        });
        displaying = tabStr;
    }
}