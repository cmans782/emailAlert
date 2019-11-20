$(document).ready(function() {
	var password_criteria_error = false;
	var password_match_error = false;

	$('#new_password').focusout(function() {
		var new_password = $(this).val();
		var regex = /(?=.{8,127})(?=.*?[^\w\s])(?=.*?[0-9])(?=.*?[A-Z])(?!.*\s)(?!.*\")(?!.*\')(?!.*\\)(?!.*\/).*?[a-z].*/g;
		// Make sure new_password matches password criteria
		if (!regex.test(new_password)) {
			// show password criteria if regex fails
			$('div[name="password-criteria-error"]').show();
			$(this).addClass('is-invalid');
			password_criteria_error = true;
		}
		else if (password_criteria_error) {
			$('div[name="password-criteria-error"]').hide();
			$(this).removeClass('is-invalid');
			password_criteria_error = false;
		}
		if ($('#confirm_new_password').val()) {
			match_passwords();
		}
	});

	$('#confirm_new_password').focusout(match_passwords);

	// validate that passwords match
	function match_passwords() {
		var new_psw = $('#new_password');
		var confirm_psw = $('#confirm_new_password');
		if (new_psw.val() != confirm_psw.val()) {
			password_match_error = true;
			$('[name="confirm_password_error"]').show();
			confirm_psw.addClass('is-invalid');
			new_psw.addClass('is-invalid');
		}
		else if (password_match_error) {
			password_match_error = false;
			$('[name="confirm_password_error"]').hide();
			confirm_psw.removeClass('is-invalid');
			new_psw.removeClass('is-invalid');
		}
	}

	$('form').submit(function(e) {
		if (password_criteria_error | password_match_error) {
			event.preventDefault();
		}
	});
});
