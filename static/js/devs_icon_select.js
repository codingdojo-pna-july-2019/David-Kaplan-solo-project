$(document).ready( function() {

	$('[name="skills_langs"]').on('click', function() {
		var tempName = $(this).find('img').attr('name');
		var count = $('#devs_skills_langs img').length;

		if ( !$('#in_'+$(this).attr('id')).prop('checked') ) {
			if ( count < 5 ) {
				$('#in_'+$(this).attr('id')).prop("checked", true);
				$('#devs_skills_langs').append($(this).find('img').clone().removeClass("icon-img").addClass("icon-img-sm"));
			} else {
				alert("You can only select 5 at a time.  Please remove one before adding another.");
			}
		} else {
			$('#in_'+$(this).attr('id')).prop("checked", false);
			$('#devs_skills_langs').find('[name="'+tempName+'"]').remove();
		} 
	});

	$('[name="skills_frameworks"]').on('click', function() {
		var tempName = $(this).find('img').attr('name');
		var count = $('#devs_skills_frameworks img').length;

		if ( !$('#in_'+$(this).attr('id')).prop('checked') ) {
			if ( count < 5 ) {
				$('#in_'+$(this).attr('id')).prop("checked", true);
				$('#devs_skills_frameworks').append($(this).find('img').clone().removeClass("icon-img").addClass("icon-img-sm"));
			} else {
				alert("You can only select 5 at a time.  Please remove one before adding another.");
			}
		} else {
			$('#in_'+$(this).attr('id')).prop("checked", false);
			$('#devs_skills_frameworks').find('[name="'+tempName+'"]').remove();
		}
	});
});