import os
from pathlib import Path

import pytest
from telegram import Update, User
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler
from unittest.mock import AsyncMock, patch, MagicMock, call
from src.database.database_handler import DatabaseHandler
from src.handlers import start, help_command, handle_profile, stop, profile_lastname, profile_city, profile_state, \
    profile_country, profile_email, profile_linkedin, profile_phone, create_profile_database, read_resume_word, \
    profile_resume_file_word, insert_data_resume_to_database, start_tailor_resume, receive_job_link_resume_creator, \
    generate_resume_file, create_cover_letter, handle_response_cover_letter_tone, receive_job_link_cover_letter_creator, \
    generate_cover_letter_file


@pytest.fixture
def db():
    test_db_url = os.getenv('TEST_DATABASE_URL')
    db_handler = DatabaseHandler(test_db_url)
    # TEST 1 - DROP TABLES
    db_handler.drop_tables()
    # TEST 2 - CREATE TABLES"
    db_handler.setup_database()
    yield db_handler
    db_handler.__del__()


@pytest.fixture
def update():
    update = AsyncMock()
    update.effective_user = User(id=12345, first_name="William", is_bot=False)
    update.message = AsyncMock()
    update.message.document = AsyncMock(file_id='file123')
    return update


@pytest.fixture
def context(db):
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    context.user_data = {
        'last_name': 'Wallace',
        'city': 'Portland',
        'state': 'OR',
        'country': 'USA',
        'email': 'william@example.com',
        'phone': '1234567890',
        'linkedin': 'www.linkedin.com/wallace'
    }
    return context

@pytest.fixture
def user_data():
    return {
        'last_name': 'Wallace',
        'city': 'Portland',
        'state': 'OR',
        'country': 'USA',
        'email': 'william@example.com',
        'phone': '1234567890',
        'linkedin': 'www.linkedin.com/wallace'
    }

@pytest.mark.asyncio
async def test_start_new_user(db, update, context):
    exists = db.check_user_exists(update.effective_user.id, update.effective_user.first_name)
    assert exists is False


@pytest.mark.asyncio
async def test_start_existing_user(db, update, context):
    exists = db.check_user_exists(update.effective_user.id, update.effective_user.first_name)
    if not exists:
        # TEST 3 - TEST ADD USER
        db.add_user(update.effective_user.id, update.effective_user.first_name)
        # TEST 4 - TEST USER DOES EXIST IN DATABASE
        exists = db.check_user_exists(update.effective_user.id, update.effective_user.first_name)
    assert exists is True


@pytest.mark.asyncio
async def test_start_return_message(db, update, context):
    user = User(id=111130, first_name="William", is_bot=False)
    update.effective_user = user
    # TEST 5 - TEST START COMMAND RETURNS MESSAGE
    await start(update, context)
    update.message.reply_html.assert_called_once()
    args, kwargs = update.message.reply_html.call_args
    assert 'Welcome' in args[0]


@pytest.mark.asyncio
async def test_help_command(db, update, context):
    user = User(id=111135, first_name="William", is_bot=False)
    update.effective_user = user
    # TEST 6 - TEST HELP COMMAND RETURNS MESSAGE
    await help_command(update, context)
    update.message.reply_text.assert_called_once()  # Change reply_html to reply_text
    args, _ = update.message.reply_text.call_args  # Same here
    assert '/start' in args[0]


LASTNAME, CITY, STATE, COUNTRY, EMAIL, PHONE, LINKEDIN, RESUME = range(8)


@pytest.mark.asyncio
@patch('src.database.database_handler.DatabaseHandler.get_status_session', new_callable=AsyncMock)
@patch('src.database.database_handler.DatabaseHandler.start_session_user')
async def test_handle_profile_active_session(mock_start_session_user, mock_get_status_session, db, update, context):
    mock_get_status_session.return_value = True
    db.add_user(update.effective_user.id, update.effective_user.first_name)
    # TEST 7 - START SESSION USER TO BE ABLE TO USE BOT
    mock_start_session_user(update.effective_user.id)
    # TEST 8 - ASSERT THAT SESSION RETURNS TRUE
    assert await db.get_status_session(update.effective_user.id) is True
    # TEST 9 - HANDLE PROFILE WHEN SESSION IS STARTED, RETURNS MESSAGE ASKING FOR LAST NAME
    await handle_profile(update, context)
    update.message.reply_text.assert_called_once()
    args, _ = update.message.reply_text.call_args
    assert 'last name' in args[0], "The message should ask for the last name but was: " + args[0]


@pytest.mark.asyncio
async def test_handle_profile_inactive_session(db, update, context):
    with patch('src.utils.user_timers', new_callable=dict):
        db.add_user(update.effective_user.id, update.effective_user.first_name)
        db.start_session_user(update.effective_user.id)
        # TEST 10 - SESSION USER FINISHED
        db.end_session_user(update.effective_user.id)
        # TEST 11 - ASSERT THE STATUS ACTIVE SESSION RETURNS FALSE
        assert db.get_status_session(update.effective_user.id) is False
        context.user_data = {}
        # TEST 12 - TEST HANDLE PROFILE WITHOUT AN ACTIVE SESSION RETURNS MESSAGE ASKING TO START SESSION
        await handle_profile(update, context)
        update.message.reply_text.assert_called_once()
        args, _ = update.message.reply_text.call_args
        assert '/start' in args[0]


@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_lastname_valid_input(user_timers_mock, update, context):
    update.message.text = "Wallace"
    # TEST 13 - ADD A PROFILE LASTNAME TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()):
        result = await profile_lastname(update, context)

    assert result == CITY
    update.message.reply_text.assert_called_once_with("What is your city?")
    assert context.user_data['last_name'] == "Wallace"


@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_city_valid_input(user_timers_mock, update, context):
    update.message.text = "Portland"
    # TEST 14 - ADD A PROFILE CITY TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()):
        result = await profile_city(update, context)
    assert result == STATE
    update.message.reply_text.assert_called_once_with("In which state do you live?")
    assert context.user_data['city'] == "Portland"

@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_state_valid_input(user_timers_mock, update, context):
    update.message.text = "OR"
    # TEST 15 - ADD A PROFILE STATE TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()):
        result = await profile_state(update, context)
    assert result == COUNTRY
    update.message.reply_text.assert_called_once_with("In which country do you live?")
    assert context.user_data['state'] == "OR"

@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_country_valid_input(user_timers_mock, update, context):
    update.message.text = "USA"
    # TEST 16 - ADD A PROFILE COUNTRY TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()):
        result = await profile_country(update, context)
    assert result == EMAIL
    update.message.reply_text.assert_called_once_with("Email")
    assert context.user_data['country'] == "USA"

@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_email_valid_input(user_timers_mock, update, context):
    update.message.text = "william@example.com"
    # TEST 17 - ADD A PROFILE EMAIL TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()):
        result = await profile_email(update, context)
    assert result == PHONE
    update.message.reply_text.assert_called_once_with("Phone number")
    assert context.user_data['email'] == "william@example.com"

@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_phone_valid_input(user_timers_mock, update, context):
    update.message.text = "1234567890"
    # TEST 18 - ADD A PROFILE EMAIL TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()):
        result = await profile_phone(update, context)
    assert result == LINKEDIN
    update.message.reply_text.assert_called_once_with("Linkedin Profile")
    assert context.user_data['phone'] == "1234567890"


@pytest.mark.asyncio
@patch('src.utils.user_timers', new_callable=dict)
async def test_profile_linkedin_valid_input(user_timers_mock, update, context):
    update.message.text = "www.linkedin.com/wallace"
    # TEST 19 - ADD A PROFILE LINKEDIN TO THE CONTEXT
    with patch('src.utils.reset_user_timer', AsyncMock()), \
            patch('src.handlers.create_profile_database', AsyncMock()):
        result = await profile_linkedin(update, context)
    assert result == RESUME
    expected_message = "Thank you for sharing your information! Now one more step. Please, add your resume in a word document so I can store your information (Make sure the titles for each section are named EDUCATION, EXPERIENCE, and SKILLS"
    update.message.reply_text.assert_called_once_with(expected_message)
    assert context.user_data['linkedin'] == "www.linkedin.com/wallace"


@pytest.mark.asyncio
async def test_create_profile_database(update, user_data):
    with patch('src.handlers.database_handler.insert_data_user') as mock_insert:
        # TEST 20 - CREATE A PROFILE WITH GIVEN INFORMATION MATCHING
        await create_profile_database(update, user_data)
        mock_insert.assert_called_once_with(
            'Wallace', 'Portland', 'OR', 'USA', 'william@example.com',
            '1234567890', 'www.linkedin.com/wallace', update.effective_user.id
        )


@pytest.mark.asyncio
@patch('src.handlers.read_resume_word', new_callable=AsyncMock)
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_profile_resume_file_word(mock_read_resume, mock_reset_timer, update, context):
    file_mock = AsyncMock()
    file_path = Path("resume.docx")
    # TEST 21 - FILE IS DOWNLOADED
    file_mock.download_to_drive = AsyncMock()
    file_mock.file_path = file_path
    context.bot.get_file.return_value = file_mock
    result = await profile_resume_file_word(update, context)
    context.bot.get_file.assert_awaited_once_with(update.message.document)
    file_mock.download_to_drive.assert_awaited_once_with(custom_path=Path("resumes/resume.docx"))
    assert result == ConversationHandler.END

@pytest.mark.asyncio
@patch('src.handlers.insert_data_resume_to_database', new_callable=AsyncMock)
@patch('src.handlers.text_extraction.extract_text_between_keywords', return_value="Sample Education")
@patch('src.handlers.text_extraction.extract_text_from_keyword_to_end', return_value="Sample Skills")
async def test_read_resume_word(mock_extract_education, mock_extract_skills, mock_insert_resume, update):
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="EDUCATION"), MagicMock(text="Sample Education"), MagicMock(text="EXPERIENCE"), MagicMock(text="Sample Skills")]
    with patch('src.handlers.Document', return_value=mock_doc):
        file_path = Path("/fakepath/fakedoc.docx")
        # TEST 22 - READ RESUME FROM WORD DOCUMENT
        await read_resume_word(update, MagicMock(), file_path)
        mock_insert_resume.assert_called_once_with('EDUCATION Sample Education EXPERIENCE Sample Skills', update)


@pytest.mark.asyncio
@patch('src.handlers.database_handler')
@patch('src.handlers.text_extraction')
async def test_insert_data_resume_to_database(mock_text_extraction, mock_database_handler, update):
    # TEST 23 - EXTRACT TEXT BETWEEN KEYWORDS IN RESUME DOC FROM USER
    mock_text_extraction.extract_text_between_keywords.side_effect = [
        "Sample Education",
        "Sample Experience"
    ]
    # TEST 24 - EXTRACT TEXT FROM KEYWORD TO 'END' KEYWORD IN RESUME DOC FROM USER
    mock_text_extraction.extract_text_from_keyword_to_end.return_value = "Sample Skills"

    mock_database_handler.add_resume.return_value = 1
    mock_database_handler.add_education = AsyncMock()
    mock_database_handler.add_work_experience = AsyncMock()
    mock_database_handler.add_skill = AsyncMock()

    document_text = "Some text EDUCATION Sample Education EXPERIENCE Sample Experience SKILLS Sample Skills"
    # TEST 25 - TEST INSERT DATA FILTERED OUT INTO DATABASE AND RESUME TABLES
    await insert_data_resume_to_database(document_text, update)
    # TEST 26 - ADD RESUME WITH ID
    mock_database_handler.add_resume.assert_called_once_with(update.effective_user.id)
    # TEST 27 - ADD EDUCATION ASSOCIATED WITH RESUME ID
    mock_database_handler.add_education.assert_called_once_with(1, "Sample Education")
    # TEST 28 - ADD EXPERIENCE ASSOCIATED WITH RESUME ID
    mock_database_handler.add_work_experience.assert_called_once_with(1, "Sample Experience")
    # TEST 29 - ADD SKILLS ASSOCIATED WITH RESUME ID
    mock_database_handler.add_skill.assert_called_once_with(1, "Sample Skills")

    calls = [
        call(document_text, "EDUCATION", "EXPERIENCE"),
        call(document_text, "EXPERIENCE", "SKILLS")
    ]
    mock_text_extraction.extract_text_between_keywords.assert_has_calls(calls, any_order=True)
    mock_text_extraction.extract_text_from_keyword_to_end.assert_called_with(document_text, "SKILLS")

WAITING_FOR_LINK_RESUME = 1

@pytest.mark.asyncio
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_start_tailor_resume(mock_reset_user_timer, mock_database_handler, update, context):
    # TEST 30 - START TAILOR RESUME WITH PROFILE PRESENT
    mock_database_handler.get_status_session.return_value = True
    mock_database_handler.get_last_resume.return_value = 1
    result = await start_tailor_resume(update, context)
    update.message.reply_text.assert_called_once_with("Please paste the link from Linkedin that contains the job")
    assert result == WAITING_FOR_LINK_RESUME



@pytest.mark.asyncio
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_start_tailor_resume_profile_not_created(mock_reset_user_timer, mock_database_handler, update, context):
    # TEST 31 - START TAILOR RESUME WITH NO PROFILE PRESENT
    mock_database_handler.get_status_session.return_value = True
    mock_database_handler.get_last_resume.return_value = 0
    result = await start_tailor_resume(update, context)
    update.message.reply_text.assert_called_once_with(
        "Please create a /profile and add a previous resume before using the resume generator")


@pytest.mark.asyncio
@patch('src.handlers.generate_resume_file', new_callable=AsyncMock)
@patch('src.handlers.linkedin_handler')
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_receive_job_link_resume_creator(mock_reset_user_timer, mock_database_handler, mock_linkedin_handler,
                                               mock_generate_resume_file, update, context):
    update.message.text = "http://linkedin.com/job/link"
    # TEST 32 - GENERATE CHAT GPT QUERY
    mock_database_handler.generate_query_chat_gpt.return_value = "resume query"
    # TEST 33 - GET JOB DESCRIPTION FROM LINKEDIN
    mock_linkedin_handler.get_job_description.return_value = "job description"
    # TEST 34 - RECEIVE THE LINK FROM USER
    result = await receive_job_link_resume_creator(update, context)

    mock_database_handler.generate_query_chat_gpt.assert_called_once_with(update.effective_user.id)
    mock_linkedin_handler.get_job_description.assert_called_once_with(update.message.text)
    mock_generate_resume_file.assert_called_once()
    assert result == ConversationHandler.END


@pytest.mark.asyncio
@patch('src.handlers.chatgpt_handler')
@patch('src.handlers.resume_creator')
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_generate_resume_file(mock_reset_user_timer, mock_database_handler, mock_resume_creator,
                                    mock_chatgpt_handler, update, context):
    mock_chatgpt_handler.resume_chatgpt_query.return_value = "generated resume content"
    mock_database_handler.get_user_by_id.return_value = {"name": "John"}

    with patch('builtins.open', new_callable=AsyncMock) as mock_open:
        mock_open.return_value.__enter__.return_value = mock_open
        # TEST 35 - GENERATE RESUME FILE
        await generate_resume_file(context, "job info", "resume info", update, update.effective_user.id)

        mock_chatgpt_handler.resume_chatgpt_query.assert_called_once()
        mock_resume_creator.create_resume.assert_called_once_with("generated resume content", {"name": "John"})
        context.bot.send_document.assert_awaited_once()
        update.message.reply_text.assert_awaited_with(
            "Thank you.\nIf you did not like the resume give it another try:\n /tailorresume \n /createcoverletter - To create a cover letter")

SELECTING_TONE = 0
WAITING_FOR_LINK_COVER = 1

@pytest.mark.asyncio
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_create_cover_letter(mock_reset_user_timer, mock_database_handler, update, context):
    mock_database_handler.get_status_session.return_value = True
    mock_database_handler.get_last_resume.return_value = 1
    # TEST 36 - START COVER LETTER CREATION WITH PROFILE CREATED
    result = await create_cover_letter(update, context)
    update.message.reply_text.assert_called_once_with("What tone do you want on your cover letter? (Very formal, Formal, Casual)")
    assert result == SELECTING_TONE

@pytest.mark.asyncio
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_create_cover_letter_profile_not_created(mock_reset_user_timer, mock_database_handler, update, context):
    mock_database_handler.get_last_resume.return_value = 0
    # TEST 37 - START COVER LETTER CREATION WITH NO PROFILE CREATED
    await create_cover_letter(update, context)
    update.message.reply_text.assert_called_once_with(
        "Please create a /profile and add a previous resume before using the cover letter generator")

@pytest.mark.asyncio
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_handle_response_cover_letter_tone(mock_reset_user_timer, update, context):
    update.message.text = "Formal"
    # TEST 38 - STORE TONE FOR COVER LETTER VALID INPUT
    result = await handle_response_cover_letter_tone(update, context)
    update.message.reply_text.assert_called_once_with(
        "Thanks for the reply. The cover letter will have a formal tone. "
        "Now, please paste the link from Linkedin that contains the job")
    assert context.user_data['tone_cover_letter'] == "formal"
    assert result == WAITING_FOR_LINK_COVER



@pytest.mark.asyncio
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_handle_response_cover_letter_tone_invalid_tone(mock_reset_user_timer, update, context):
    update.message.text = "Relaxed"
    # TEST 39 - STORE TONE FOR COVER LETTER INVALID INPUT
    result = await handle_response_cover_letter_tone(update, context)
    update.message.reply_text.assert_called_once_with("Please enter very formal, formal, or casual")
    assert result == SELECTING_TONE


@pytest.mark.asyncio
@patch('src.handlers.generate_cover_letter_file', new_callable=AsyncMock)
@patch('src.handlers.linkedin_handler')
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_receive_job_link_cover_letter_creator(mock_reset_user_timer, mock_database_handler,
                                                     mock_linkedin_handler, mock_generate_cover_letter_file, update,
                                                     context):
    context.user_data['tone_cover_letter'] = "formal"
    update.message.text = "http://linkedin.com/job/link"
    # TEST 40 - GENERATE QUERY CHATGPT FOR COVER LETTER
    mock_database_handler.generate_query_chat_gpt.return_value = "resume query"
    mock_linkedin_handler.get_job_description.return_value = "job description"
    # TEST 41 - GET THE LINK FOR JOB DESCRIPTION TO CREATE COVER LETTER
    result = await receive_job_link_cover_letter_creator(update, context)

    mock_linkedin_handler.get_job_description.assert_called_once_with(update.message.text)
    mock_generate_cover_letter_file.assert_called_once()
    assert result == ConversationHandler.END


@pytest.mark.asyncio
@patch('src.handlers.chatgpt_handler')
@patch('src.handlers.cover_letter_creator')
@patch('src.handlers.database_handler')
@patch('src.utils.reset_user_timer', new_callable=AsyncMock)
async def test_generate_cover_letter_file(mock_reset_user_timer, mock_database_handler, mock_cover_letter_creator,
                                          mock_chatgpt_handler, update, context):
    mock_chatgpt_handler.cover_letter_chatgpt_query.return_value = "generated cover letter content"
    mock_database_handler.get_user_by_id.return_value = {"name": "William"}

    with patch('builtins.open', new_callable=AsyncMock) as mock_open:
        mock_open.return_value.__enter__.return_value = mock_open
        # TEST 42 - GENERATE COVER LETTER DOCUMENT FOR USER
        await generate_cover_letter_file(update, context, "job info", "resume info", update.effective_user.id, "formal")

        mock_chatgpt_handler.cover_letter_chatgpt_query.assert_called_once()
        mock_cover_letter_creator.create_cover_letter.assert_called_once_with("generated cover letter content",
                                                                              {"name": "William"})
        context.bot.send_document.assert_awaited_once()
        update.message.reply_text.assert_awaited_with(
            "Thank you.\nIf you did not like the cover letter give it another try:\n"
            "/tailorresume - To generate a resume\n"
            "/createcoverletter - To create a cover letter")