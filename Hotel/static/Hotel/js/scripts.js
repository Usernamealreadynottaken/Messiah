var currentHeight = $(".additions").height();
$(".additions").css("height", "100px");

function animateAdditions() {
    if ($(".additions").height() > 100) {
        $(".additions").animate({
            "height": "100",
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

$(".rooms").change(function() {
    var value = $(".rooms option:selected").val();
    if (value == 1) {
        $(".room2").animate({opacity: 0});
        $(".room2").css("display", "none");
        $(".room3").animate({opacity: 0});
        $(".room3").css("display", "none");
    } else if (value == 2) {
        $(".room2").animate({opacity: 1});
        $(".room2").css("display", "table-row");
        $(".room3").animate({opacity: 0});
        $(".room3").css("display", "none");
    } else if (value == 3) {
        $(".room2").animate({opacity: 1});
        $(".room2").css("display", "table-row");
        $(".room3").animate({opacity: 1});
        $(".room3").css("display", "table-row");
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

$( document ).ready(function() {
  $('.tab-content .nav a').on('click', function(event){
    event.preventDefault();
    $('html,body').animate({scrollTop:$(this.hash).offset().top}, 500);
  });

  $(window).scroll(function (){
    if($(this).scrollTop() > 600){
        $('.scroll-up').fadeIn();
    } else{
        $('.scroll-up').fadeOut();
    }
  });

  $('.scroll-up').click(function (){
    $("html, body").animate({
        scrollTop: 0
    }, 600);
    return false;
  });

});