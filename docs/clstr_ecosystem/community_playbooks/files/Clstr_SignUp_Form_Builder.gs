/**
 * CLSTR VIZAG COMMUNITY — SIGN-UP FORM BUILDER
 * ---------------------------------------------
 * HOW TO USE:
 * 1. Go to script.google.com → New Project
 * 2. Paste this entire file in, replacing the default code
 * 3. Click Run ▶ on buildClstrSignupForm()
 * 4. Authorize when prompted (this is your own script, running on your own account)
 * 5. Check the Execution Log (View → Logs) for the live form URL + edit URL
 *
 * This creates a real, working Google Form with:
 * - Two-path student verification (college email OR roll number + ID upload)
 * - Full Guild + Circle taxonomy (5 Guilds, 11 Circles, dual-tagged items flagged)
 * - Branching logic so students only see the fields relevant to their path
 */

function buildClstrSignupForm() {
  const form = FormApp.create('Clstr Vizag Community — Sign Up');
  form.setDescription(
    "Vizag's first verified, cross-college student community. " +
    "Takes about 3 minutes. Everything here stays private and is only used to confirm you're a real student."
  );
  form.setCollectEmail(false); // we handle email ourselves via Q-fields below
  form.setProgressBar(true);

  // ---------- SECTION 1: BASICS ----------
  form.addSectionHeaderItem()
    .setTitle('The Basics')
    .setHelpText('Just the essentials.');

  const nameItem = form.addTextItem();
  nameItem.setTitle('Full name').setRequired(true);

  const collegeItem = form.addListItem();
  collegeItem.setTitle('Which college are you at?')
    .setRequired(true)
    .setChoiceValues([
      // P0
      'Raghu Engineering College', 'Andhra University', 'GITAM (Deemed University)',
      // P1
      'ANITS', 'GVPCE', 'VIIT', 'Raghu Institute of Technology (RIT)',
      'KL University Visakhapatnam', 'MVGR College of Engineering', 'NSRIT',
      // P2
      'BVRIT', 'Avanthi Institute of Engineering & Technology', 'Chaitanya Engineering College',
      'IIPE', 'Pydah College of Engineering & Technology', 'VIEW (Women\'s Engineering)',
      'Sri Chaitanya Engineering College', 'DIET', 'Swarnandhra College of Engineering',
      // Non-engineering streams — Law / Medical / Management / Arts
      'Law college (please specify in next field)',
      'Medical / Dental / Pharmacy college (please specify)',
      'Management / Maritime college (please specify)',
      'Arts / Science / Education college (please specify)',
      'My college is not listed here'
    ]);

  const collegeOtherItem = form.addTextItem();
  collegeOtherItem.setTitle('If you selected "not listed" or a stream category above, name your exact college here')
    .setRequired(false);

  const yearItem = form.addListItem();
  yearItem.setTitle('Year of study')
    .setRequired(true)
    .setChoiceValues(['1st year', '2nd year', '3rd year', '4th year', '5th year (Law/Pharmacy/Medical)', 'Final year', 'Recent alumni']);

  const branchItem = form.addTextItem();
  branchItem.setTitle('Branch / stream (e.g. CSE, ECE, B.Com, BA LLB, MBBS, B.Pharm, Nautical Science)')
    .setRequired(true);

  // ---------- SECTION 2: VERIFICATION (BRANCHING) ----------
  const verifySection = form.addPageBreakItem().setTitle('Verifying You\'re a Real Student');

  const verifyChoice = form.addMultipleChoiceItem();
  verifyChoice.setTitle('How can we verify you\'re a real student?')
    .setRequired(true)
    .setHelpText('Pick whichever applies to you — both paths are treated equally.');

  // Create the two destination pages BEFORE wiring choices to them
  const emailPage = form.addPageBreakItem().setTitle('College Email Verification');
  const emailItem = form.addTextItem();
  emailItem.setTitle('Your college email address')
    .setRequired(true)
    .setHelpText('This is how we verify you\'re a real student. It stays private and is never shown publicly.')
    .setValidation(FormApp.createTextValidation()
      .requireTextIsEmail()
      .build());

  const mergePage1 = form.addPageBreakItem().setTitle('Almost Done');

  const rollPage = form.addPageBreakItem().setTitle('Roll Number Verification');
  const rollItem = form.addTextItem();
  rollItem.setTitle('College registration / roll number')
    .setRequired(true)
    .setHelpText('The number on your ID card or admit card — e.g. 21A91A0501, 321106510001. Stays private, only used to confirm enrollment.');
  const idUploadItem = form.addFileUploadItem();
  idUploadItem.setTitle('Upload a photo of your student ID card or admit card')
    .setRequired(true)
    .setHelpText('Confirms your roll number matches a real enrollment. Reviewed within 48 hours, never shared publicly.')
    .setMaxFiles(1)
    .setMaxFileSize(10 * 1024 * 1024) // 10MB
    .setFileTypes([FormApp.FileType.IMAGE, FormApp.FileType.DOCUMENT]);

  const mergePage2 = form.addPageBreakItem().setTitle('Almost Done');

  // Wire the branching: choice 1 -> emailPage, choice 2 -> rollPage
  verifyChoice.setChoiceValues(['I have a college email address', 'My college doesn\'t give me one — I\'ll use my registration/roll number']);
  const choices = [
    verifyChoice.createChoice('I have a college email address', emailPage),
    verifyChoice.createChoice('My college doesn\'t give me one — I\'ll use my registration/roll number', rollPage),
  ];
  verifyChoice.setChoices(choices);

  // Both branches route to the same "Almost Done" merge -> personal email + rest of form
  emailPage.setGoToPage(mergePage1);
  rollPage.setGoToPage(mergePage2);

  // ---------- SECTION 3: PERSONAL EMAIL (shown after either branch) ----------
  // Note: Google Forms requires this to be duplicated logically since each page-break
  // routes independently. We add it once on the shared "Almost Done" flow below by
  // pointing both merge pages to the same next section start.

  const contactSection = form.addPageBreakItem().setTitle('How to Reach You');
  const personalEmailItem = form.addTextItem();
  personalEmailItem.setTitle('Personal email (for account access)')
    .setRequired(true)
    .setHelpText('Since not all colleges provide student email, we\'ll use this to reach you — Gmail, Outlook, whatever you actually check.')
    .setValidation(FormApp.createTextValidation().requireTextIsEmail().build());

  const phoneItem = form.addTextItem();
  phoneItem.setTitle('Phone / WhatsApp number')
    .setRequired(true)
    .setHelpText('For your college WhatsApp group and event updates.');

  // Route both merge pages into this shared contact section
  mergePage1.setGoToPage(contactSection);
  mergePage2.setGoToPage(contactSection);

  // ---------- SECTION 4: GUILDS (skill/collab-oriented) ----------
  const guildSection = form.addPageBreakItem().setTitle('Guilds — What You Build');
  const guildItem = form.addCheckboxItem();
  guildItem.setTitle('Guilds — pick any that fit (skill / collab focused)')
    .setHelpText('Not exclusive — pick as many as apply. This helps us match you with the right people and projects.')
    .setChoiceValues([
      'Build Guild — coders, engineers, product-minded builders',
      'Design Guild — graphic design, UI/UX, video editing, photography',
      'Create Guild — content creators, writers, podcasters, meme-page runners',
      'Hustle Guild — business, marketing, side-hustlers, aspiring founders',
      'Grow Guild — career-focused, mentorship-seeking (good if you\'re still deciding)',
      'None of these — I\'m here mainly for the social side',
    ])
    .setRequired(false);

  // ---------- SECTION 5: CIRCLES (pure social/interest, zero performance bar) ----------
  const circleSection = form.addPageBreakItem().setTitle('Circles — What You\'re Into');
  const circleItem = form.addCheckboxItem();
  circleItem.setTitle('Circles — pick any that fit (pure interest, zero performance bar)')
    .setHelpText('No skill or output required for any of these — just show up because you\'re into it.')
    .setChoiceValues([
      'Foodies',
      'Music',
      'Sports & Fitness',
      'Travel & Explore / Beach Crew',
      'Movies & Anime',
      'Book Club',
      'New to Vizag (outstation / non-local students)',
      'Esports (competitive gaming — Valorant, BGMI, etc.)',
      'Performing Arts (dance, music, theatre — classical or contemporary)',
      'Debate, MUN & Quiz',
      'Volunteering & Impact (NGO work, blood donation, teaching)',
      'Competitive Exams (GATE / CAT / NEET-PG / UPSC — peer accountability, not tutoring)',
      'Auto & Bike Crew',
    ])
    .setRequired(false);

  // ---------- SECTION 6: CLOSING ----------
  const closingSection = form.addPageBreakItem().setTitle('Last Thing');
  const howHeardItem = form.addListItem();
  howHeardItem.setTitle('How did you hear about Clstr Vizag?')
    .setRequired(false)
    .setChoiceValues(['A friend', 'College WhatsApp group', 'Instagram', 'Campus Captain / Ambassador', 'An event', 'Other']);

  const agreeItem = form.addCheckboxItem();
  agreeItem.setTitle('Before you go')
    .setRequired(true)
    .setChoiceValues(['I confirm I\'m a genuine student and the info above is accurate']);

  Logger.log('Form created successfully.');
  Logger.log('Live form URL: ' + form.getPublishedUrl());
  Logger.log('Edit URL (for you only): ' + form.getEditUrl());
}
