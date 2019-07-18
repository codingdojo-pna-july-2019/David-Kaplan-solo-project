$(document).ready( function() {

	$('[name="skills_langs"]').on('click', function() {
		var count = document.querySelectorAll('[name="dev_lang_input"]:checked').length;

		if ( !$('#in_'+$(this).attr('id')).prop('checked') ) {
			if ( count < 5 ) {
				$('#in_'+$(this).attr('id')).prop("checked", true);
			} else {
				alert("You can only select 5 at a time.  Please remove one before adding another.");
			}
		} else {
			$('#in_'+$(this).attr('id')).prop("checked", false);
		} 
	});

	$('[name="skills_frameworks"]').on('click', function() {
		var count = document.querySelectorAll('[name="dev_framework_input"]:checked').length;

		if ( !$('#in_'+$(this).attr('id')).prop('checked') ) {
			if ( count < 5 ) {
				$('#in_'+$(this).attr('id')).prop("checked", true);
			} else {
				alert("You can only select 5 at a time.  Please remove one before adding another.");
			}
		} else {
			$('#in_'+$(this).attr('id')).prop("checked", false);
		}
	});
});