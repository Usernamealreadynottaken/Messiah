$(".rezerwacje_class").addClass("selected");

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

function validateDate(date, error) {
    var regEx  = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    if(regs = date.match(regEx)) {
        if (regs[1] > 12) {
            $(error).text("Nie ma takiego miesiaca.");
            return false;
        } else {
            if ((regs[1] == 1 || regs[1] == 3 || regs[1] == 5 ||
                    regs[1] == 7 || regs[1] == 8 || regs[1] == 10 ||
                    regs[1] == 12) && regs[2] > 31) {
                    $(error).text("Nie ma takiego dnia.");
                return false
            } else if ((regs[1] == 4 || regs[1] == 6 || regs[1] == 9 ||
                regs[1] == 11) && regs[2] > 30) {
                $(error).text("Nie ma takiego dnia.");
                return false;
            } else if (regs[1] == 2 && regs[2] > 28) {

                var year = regs[3];
                if (year % 4 ==  0 && year % 100 != 0 || year % 400 == 0 && regs[2] == 29) {
                    $(error).text("");
                    return true;
                }
                $(error).text("Nie ma takiego dnia.");
                return false;
            }
        }
    } else {
        $(error).text("Data musi byc w formacie: mm/dd/yyyy.");
        return false;
    }
    $(error).text("");
    return true;
}

$(".change-calendar").click(function() {
    if ($(".calendar-from").is(':visible')) {
        $(".calendar-from").fadeOut();
        $(".calendar-to").fadeIn();
        $("change-calendar").html("Wybierz date wyjazdu: ");
    } else {
        $(".calendar-to").fadeOut();
        $(".calendar-from").fadeIn();
        $("change-calendar").html("Wybierz date przyjazdu: ");
    }
});

$( window ).resize(function() {
    if ($(".reservations-content").width() > 885) {
        $(".calendar-to").css("display", "");
        $(".calendar-from").css("display", "");
    }
});