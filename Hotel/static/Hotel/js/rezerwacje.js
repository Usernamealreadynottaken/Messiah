$(".rezerwacje_class").addClass("selected");
disableInputs($(".reservations-content").width());

$(".rooms-select").change(function() {
    sprawdzPoprawnosc();
    $(".NoRooms").html( $(".rooms").val() );
});

$(".date-from").change(function() {
    updateNights();
});

$(".date-to").change(function() {
    updateNights();
});

$(document).ready(function() {
    $(".rooms-select").trigger("change");
    $(".date-from").trigger("change");
});

function updateNights() {
    var days = $(".date-from").val().substring(3,5);
    var months = $(".date-from").val().substring(0, 2) - 1;
    var years = $(".date-from").val().substring(6);
    var dateFrom = new Date(years, months, days);

    days = $(".date-to").val().substring(3,5);
    months = $(".date-to").val().substring(0, 2) - 1;
    years = $(".date-to").val().substring(6);
    var dateTo = new Date(years, months, days);

    var diff = (dateTo - dateFrom) / 86400000;
    if (diff <= 0) {
        $(".NoNights").html("-");
    } else {
        $(".NoNights").html(diff);
    }
}

function validateName(input) {
    if ($(input).val() == "") {
        $(input).parent().removeClass("positive-input");
        $(input).parent().addClass("negative-input");
        $(".name-error").animate({
            "height": "28px",
        });
        return false;
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        $(".name-error").animate({
            "height": "0",
        });
        return true;
    }
}

function validateEmail(input) {
    var regEx = /^[a-zA-Z0-9!#$%&\'*+\-\/=?^_`{|}~]+(\.?[a-zA-Z0-9!#$%&'*+\-\/=?^_`{|}~]+)*@[a-zA-Z0-9]+((\.|\-)?[a-zA-Z0-9]+)*\.[a-zA-Z0-9]+$/;
    var email = $(input).val();
    var atPosition = email.indexOf("@");
    var dotPosition = email.lastIndexOf(".");
    if ($(input).val() == "" ||
     (atPosition < 1 || dotPosition < atPosition+2 || dotPosition+2 >= email.length) ||
     !email.match(regEx)) {
        $(input).parent().removeClass("positive-input");
        $(input).parent().addClass("negative-input");
        $(".email-error").animate({
            "height": "28px",
        });
        return false;
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        $(".email-error").animate({
            "height": "0",
        });
        return true;
    }
}

$('input[name=name]').focusout(function() {
    validateName($(this));
});

$('input[name=email]').focusout(function() {
    validateEmail($(this));
});

function disableInputs(w) {
    if (w < 634) {
        $(".from-overlay").css("display", "block");
        $(".to-overlay").css("display", "block");
    } else {
        $(".from-overlay").css("display", "none");
        $(".to-overlay").css("display", "none");
    }
}

$( window ).resize(function() {
    var w = $(".reservations-content").width();
    if (w > 885 || w < 634) {
        $(".calendar-to").css("display", "");
        $(".calendar-from").css("display", "");
    }
    disableInputs(w);
});