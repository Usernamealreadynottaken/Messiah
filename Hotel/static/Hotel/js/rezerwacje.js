

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
    var currentDate = new Date();
    currentDate.setDate(currentDate.getDate() -1);
    var days = $(".datepicker-from").datepicker("getDate").getDate();
    var months = $(".datepicker-from").datepicker("getDate").getMonth();
    var years = $(".datepicker-from").datepicker("getDate").getFullYear();
    var dateFrom = new Date(years, months, days);
    if (currentDate < dateFrom) {
        days = $(".datepicker-to").datepicker("getDate").getDate();
        months = $(".datepicker-to").datepicker("getDate").getMonth();
        years = $(".datepicker-to").datepicker("getDate").getFullYear();
        var dateTo = new Date(years, months, days);
        if (dateFrom <= dateTo) {
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
        } else {
            $(".success").html("Bledne daty!");
        }
    }
})