// This file was automatically generated from instructor_microscopy_page1.soy.
// Please don't edit this file by hand.

if (typeof scb_instructor_microscopy_page1 == 'undefined') { var scb_instructor_microscopy_page1 = {}; }


scb_instructor_microscopy_page1.main = function(opt_data, opt_sb) {
  var output = opt_sb || new soy.StringBuilder();
  output.append('<div class=\'scb_s_microscopy_view\' >');
  scb_instructor_homepage.display_header(opt_data, output);
  scb_instructor_common.assignment_step({step: 1, last_step: opt_data.last_step, prev_step: opt_data.prev_step, assignments: assignments}, output);
  output.append('<div class=\'scb_s_microscopy_container\' role=\'main\'>');
  scb_instructor_homepage.display_assignment_navigation(opt_data, output);
  scb_instructor_microscopy_page1.display_assignment(opt_data, output);
  output.append('</div>');
  scb_instructor_homepage.display_footer(opt_data, output);
  output.append('</div>');
  return opt_sb ? '' : output.toString();
};


scb_instructor_microscopy_page1.display_assignment = function(opt_data, opt_sb) {
  var output = opt_sb || new soy.StringBuilder();
  output.append('<div class=\'scb_s_course_setup_description \'><div class=\'scb_s_abstract_title\'>Assignment Editor</div><div class=\'scb_s_experiment_setup_title\'>Microscopy Page1</div><div><button assignment_id=\'', soy.$$escapeHtml(opt_data.assignment.id), '\' class=" scb_f_microscopy_page1_save_assignment_button scb_s_assignment_setup_save_button scb_s_navigation_button"  aria-label=\'Save and Continue\' role=\'button\'>SAVE AND CONTINUE &nbsp; &#9654;</button></div></div>');
  return opt_sb ? '' : output.toString();
};
