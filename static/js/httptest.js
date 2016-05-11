$(document).ready(function() {


	console.log("ready");

	;
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

	var x = $('a#sendmail').attr('href');
	$('a#sendmail').attr('href',x+"?sendmail&testid="+mytestid);


	csrftoken = $("input[name*='csrfmiddlewaretoken'").attr("value");
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	});

	$("button#runTest").click(function(e) {
		e.preventDefault();
		var url_data = $("input#url");
		data = $("#testForm").serialize();
		$.ajax({
			data: data,
			success: function(data) {
				location.reload(true);
			},
			error: function() {},
			processData: false,
			type: 'POST',
			url: '/fastapp/api/username/'+window.user+'/base/httptest/apy/entrypoint/execute/?data_from=payload&json=&testid=' + mytestid + "&version=" + version
		});
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
			url: '/fastapp/api/username/'+window.user+'/base/httptest/apy/entrypoint/execute/?data_from=payload&json=&action=reset&testid=' + mytestid + "&version=" + version
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
			url: '/fastapp/api/base/httptest/apy/entrypoint/execute/?data_from=payload&json=&action=delete&shared_key=e31709b5-f163-4219-908d-ba5abb482e5d&testid=' + mytestid + "&version=" + version
		});
	});



});
