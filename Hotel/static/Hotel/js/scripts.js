$(".datepicker-from").datepicker({altField: ".date-from"});
$(".datepicker-to").datepicker({
    altField: ".date-to",
});

$(".rooms").change(function() {
    var value = $(".rooms option:selected").val();
    if (value == 1) {
        $(".room2").fadeOut();
        $(".room3").fadeOut();
    } else if (value == 2) {
        $(".room2").fadeIn();
        $(".room3").fadeOut();
    } else if (value == 3) {
        $(".room2").fadeIn();
        $(".room3").fadeIn();
    }
});