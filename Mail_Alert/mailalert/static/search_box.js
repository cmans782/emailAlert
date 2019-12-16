allow_submit = true;

// validate student ID entered
$('#student_id').focusout(function(e) {
	var url = '/home/search_student'; // send the form data here.
	$.ajax({
		type : 'POST',
		url  : url,
		data : { student_id: $('#student_id').val() }
	}).done(function(data) {
		if (data.error) {
			$('#student_id').addClass('is-invalid');
			$('#search-error').show();
			$('#search-error span').text(data.error);
			allow_submit = false;
		}
		else {
			allow_submit = true;
			$('#student_id').removeClass('is-invalid');
			$('#search-error').hide();
		}
	});
	e.preventDefault(); // block the traditional submission of the form.
});

$('#submit').click(function(e) {
	// make sure the user entered something in the search bar
	if ($('#student_id').val() == '') {
		$('#student_id').addClass('is-invalid');
		$('#search-error span').text('Please enter a student ID');
		$('#search-error').show();
		$('#student_id').focus();
		e.preventDefault(e);
	}
	// this will be false if the id they entered does not belong to a student
	if (!allow_submit) {
		$('#student_id').focus();
		e.preventDefault(e);
	}
});

// autocomplete for search bar
$('[name="student_id"]').focus(function() {
	$(this).autocomplete({
		source    : function(request, response) {
			$.ajax({
				url     : '/newPackage/suggestions',
				data    : {
					search_bar : request.term
				},
				success : function(data) {
					response(data);
				}
			});
		},
		// only make request if two characters have been typed in
		minLength : 3
	});
});
$('#student_id').focus();
