var currentHeight = $(".additions").height();
$(".additions").css("height", "75px");

function animateAdditions() {
    if ($(".additions").height() > 75) {
        $(".additions").animate({
            "height": "75",
        }, 500, "easeInOutQuad");
        $('.additions h2 img').animateRotate(-180, -360, 500, 'easeInSine', null);
    } else {
        $(".additions").animate({
            "height": currentHeight,
        }, 500, "easeInOutQuad");
        $('.additions h2 img').animateRotate(0, -180, 500, 'easeInSine', null);
    }
}

$.fn.animateRotate = function(startAngle, endAngle, duration, easing, complete){
    return this.each(function(){
        var elem = $(this);

        $({deg: startAngle}).animate({deg: endAngle}, {
            duration: duration,
            easing: easing,
            step: function(now){
                elem.css({
                  '-moz-transform':'rotate('+now+'deg)',
                  '-webkit-transform':'rotate('+now+'deg)',
                  '-o-transform':'rotate('+now+'deg)',
                  '-ms-transform':'rotate('+now+'deg)',
                  'transform':'rotate('+now+'deg)'
                });
            },
            complete: complete || $.noop
        });
    });
};

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

$(".additions h2").click(function() {
    animateAdditions();
});

$( "#clickme" ).click(function() {
  $( "#book" ).animate({
    opacity: 0.25,
    left: "+=50",
    height: "toggle"
  }, 5000, function() {
    // Animation complete.
  });
});