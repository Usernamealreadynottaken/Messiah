
$(".rooms").change(function() {
    sprawdzPoprawnosc();
})

$(".adults1").change(function() {
    sprawdzPoprawnosc();
})

$(".adults2").change(function() {
    sprawdzPoprawnosc();
})

$(".adults3").change(function() {
    sprawdzPoprawnosc();
})

$(".kids1").change(function() {
    sprawdzPoprawnosc();
})

$(".kids2").change(function() {
    sprawdzPoprawnosc();
})

$(".kids3").change(function() {
    sprawdzPoprawnosc();
})

$(".send").click(function() {
    $("form").ajaxForm(function(data) {
        var parsed = $.parseJSON(data);

        if (parsed["message"] && parsed["message"] == "success") {
            if (parsed["kod"]) {
                $(".success").html("Udalo sie zarezerwowac!<br /><br >Twoj kod rezerwacji to: " + parsed["kod"]);
            } else {
                $(".success").html("Udalo sie zarezerwowac!<br /><br >Serwer nie wyslal kodu rezerwacji!");
            }
        } else if (parsed["message"] && parsed["message"] == "validation_error") {
            $(".success").html("Nie mozna zarezerwowac tego pokoju na ten termin.");
        } else if (parsed["message"] && parsed["message"] == "site_error") {
            $(".success").html("Serwer otrzymal uszkodzone dane.");
        } else {
            $(".success").html("Stalo sie cos czego nawet programista nie przewidzial.");
        }
    });
    $("form").submit();
})

function validateName(input) {
    if ($(input).val() == "") {
        $(input).parent().removeClass("positive-input");
        $(input).parent().addClass("negative-input");
        $(".name-error").animate({
            "height": "28px",
        });
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        $(".name-error").animate({
            "height": "0",
        });
    }
}

function validateEmail(input) {
    var email = $(input).val();
    var atPosition = email.indexOf("@");
    var dotPosition = email.lastIndexOf(".");
    if ($(input).val() == "" ||
    (atPosition < 1 || dotPosition < atPosition+2 || dotPosition+2 >= email.length)) {
        $(input).parent().removeClass("positive-input");
        $(input).parent().addClass("negative-input");
        $(".email-error").animate({
            "height": "28px",
        });
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        $(".email-error").animate({
            "height": "0",
        });
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