function validateName(input) {
    if ($(input).val() == "") {
        $(input).parent().removeClass("positive-input");
        $(input).parent().addClass("negative-input");
        return false;
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        return true;
    }
}

function validateContent(textarea) {
    if ($(textarea).val() == "") {
        $(textarea).parent().removeClass("positive-input");
        $(textarea).parent().addClass("negative-input");
        return false;
    } else {
        $(textarea).parent().removeClass("negative-input");
        $(textarea).parent().addClass("positive-input");
        return true;
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
        return false;
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        return true;
    }
}

$('input[name=name]').focusout(function() {
    validateName($(this));
});

$('input[name=email]').focusout(function() {
    validateEmail($(this));
});

$('textarea[name=tresc]').focusout(function() {
    validateContent($(this));
});