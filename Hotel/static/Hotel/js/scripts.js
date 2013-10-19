var currentHeight = $(".additions").height();
$(".additions").css("height", "75px");

function animateAdditions() {
    if ($(".additions").height() > 75) {
        $(".additions").animate({
            "height": "75",
        }, 500, "easeInOutQuad");
        $('.additions h2 img').animate({  borderSpacing: -180 }, {
            step: function(now,fx) {
              $(this).css('-webkit-transform','rotate('+now+'deg)');
              $(this).css('-moz-transform','rotate('+now+'deg)');
              $(this).css('-ms-transform','rotate('+now+'deg)');
              $(this).css('-o-transform','rotate('+now+'deg)');
              $(this).css('transform','rotate('+now+'deg)');
            },
            duration: 500
        },'linear');
    } else {
        $(".additions").animate({
            "height": currentHeight,
        }, 500, "easeInOutQuad");
        $('.additions h2 img').animate({  borderSpacing: -180 }, {
            step: function(now,fx) {
              $(this).css('-webkit-transform','rotate('+now+'deg)');
              $(this).css('-moz-transform','rotate('+now+'deg)');
              $(this).css('-ms-transform','rotate('+now+'deg)');
              $(this).css('-o-transform','rotate('+now+'deg)');
              $(this).css('transform','rotate('+now+'deg)');
            },
            duration: 500
        },'linear');
    }
}

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