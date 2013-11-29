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
        return false;
    } else {
        $(input).parent().removeClass("negative-input");
        $(input).parent().addClass("positive-input");
        return true;
    }
}

$('input[name=news-email]').focusout(function() {
    validateEmail($(this));
});