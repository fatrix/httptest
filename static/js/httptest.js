$(document).ready(function() {
    (function($) {
        $.extend({
            getQueryString: function(name) {
                function parseParams() {
                    var params = {},
        e,
        a = /\+/g, // Regex for replacing addition symbol with a space
        r = /([^&=]+)=?([^&]*)/g,
        d = function(s) {
            return decodeURIComponent(s.replace(a, " "));
        },
        q = window.location.search.substring(1);

        while (e = r.exec(q))
            params[d(e[1])] = d(e[2]);

        return params;
                }

                if (!this.queryStringParams)
            this.queryStringParams = parseParams();

                return this.queryStringParams[name];
            }
        });
    })(jQuery);

    //testid = get("testid");
    //
    var mytestid = $.getQueryString('testid');
    var version = $.getQueryString('version');
    $("h1#testid").text(mytestid);
    // $("h1#version").text("RUNTIME-VERSION: " + version);

    /*$( "button#sendmail" ).click(function() {

        $(this).prop('disabled', true);
        $("#email").prop('disabled', true);

        var that = this;
        email = $("#email").val();
        //window.open(base_url+"?sendmail&email="+email);
        email_url = base_url+"?sendmail&email="+email;


        $.ajax({
            success: function(data) {
                $(that).text("Mail sent")
            $(that).removeClass("btn-primary");
        $(that).addClass("btn-success");
        $("#email").val("");
            },
            error: function(xhr) {
                $(that).prop('disabled', false);
                $("#email").prop('disabled', false);
                $(that).text("ErroErrorr")
            },
            processData: false,
            type: 'GET',
            url: email_url
        });

    });
    */

    csrftoken = $("input[name*='csrfmiddlewaretoken']").attr("value");
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    if (window.api_url == null){
        base_url = '/userland/'+window.user+'/httptest/api/apy/entrypoint/execute/?';
    } else {
        base_url = window.api_url +"?";
    }

    function reload() {
        location.reload(true);
    };

    $("button#runTest").click(function(e) {
        var that = this;
        var orig_text = $(this).text();
        e.preventDefault();
        $("#buttons > div").remove();

        $(this).prop('disabled', true);
        $(this).text("Test running...");

        var url_data = $("input#url");
        data = $("#testForm").serialize();
        run = function(data, base_url, mytestid, version) {
            $.ajax({ data: data, success: function(data) { if (data['status'] != "RUNNING") {
                        $("button#runTest").text("Reloading page...");
                        setTimeout(reload, 2000);
                    } else {
                        //url = data.url;
                        //base_url = base_url+"?rid="+data.rid;
                        if (base_url.indexOf("rid=") == -1) {
                            url = base_url + "rid=" + data.rid + "&";
                        }
                        setTimeout(function() {
                            run(data, url, mytestid, version);
                        }, 3000);
                    }
                }, error: function(xhr) {
                    $(that).prop('disabled', false);
                    $(that).text(orig_text);
                    try {
                        var txt = '<div class="alert alert-danger"> <strong>Error! </strong>' + JSON.parse(xhr.responseText).exception_message + '</div>';
                    } catch(err) {
                        var txt = '<div class="alert alert-danger"> <strong>Error! </strong>' + "Unknown Error" + '</div>';
                    }
                    $("div#buttons").append(txt);
                },
                processData: false,
                type: 'POST',
                url: base_url + 'async=&data_from=payload&json=&testid=' + mytestid + "&version=" + version
            });

        }
        run(data, base_url, mytestid, version)
        });
    $("button#reset").click(function(e) {
        e.preventDefault();
        $.ajax({
            success: function(data) {
                location.reload(true);
            },
            error: function() {},
            processData: false,
            type: 'POST',
            url: base_url + 'data_from=payload&json=&action=reset&testid=' + mytestid + "&version=" + version
        });
    });
    $("button#delete").click(function(e) {
        e.preventDefault();
        $.ajax({
            success: function(data) {
                location.reload(true);
            },
            error: function() {},
            processData: false,
            type: 'POST',
            url: base_url + 'data_from=payload&json=&action=delete&shared_key=e31709b5-f163-4219-908d-ba5abb482e5d&testid=' + mytestid + "&version=" + version
        });
    });

});
