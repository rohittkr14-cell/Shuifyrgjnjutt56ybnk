from telethon import TelegramClient, events
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    InviteToChannelRequest,
    EditAdminRequest,
    EditPhotoRequest,
    DeleteChannelRequest
)
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import (
    ChatAdminRights,
    InputChatUploadedPhoto,
    MessageActionChatAddUser,
    MessageActionChatJoinedByLink,
    MessageActionChatEditPhoto,
    MessageActionChatEditTitle,
    MessageActionChatDeletePhoto
)
import asyncio

# ── Config ────────────────────────────────────────────────────────────────
api_id = 34365075
api_hash = "23c4c0cd9fef652b967d9f2b66cbf560"

CREATEGROUP_ADMIN = "Shuify"

PFP1 = "Pfp1.jpg"

# ── YAHAN BOT KA USERNAME DAALO ─────────────────────────────────────────
BOT_USERNAME = "@Secureblebot"
BOT_TITLE = "Secureble Bot"

DEAL_START = 274

# ── Admin rights for Shuify (anonymous OFF) ─────────────────────────────
admin_rights_shuify = ChatAdminRights(
    change_info=True,
    post_messages=True,
    edit_messages=True,
    delete_messages=True,
    ban_users=True,
    invite_users=True,
    pin_messages=True,
    add_admins=True,
    anonymous=False,        # ❌ Shuify ke liye anonymous OFF
    manage_call=True
)

# ── Admin rights for Owner (anonymous ON) ───────────────────────────────
admin_rights_owner = ChatAdminRights(
    change_info=True,
    post_messages=True,
    edit_messages=True,
    delete_messages=True,
    ban_users=True,
    invite_users=True,
    pin_messages=True,
    add_admins=True,
    anonymous=True,         # ✅ Owner ke liye anonymous ON
    manage_call=True
)

client = TelegramClient("session", api_id, api_hash)
deal_counter = DEAL_START

# ── Admin list ────────────────────────────────────────────────────────────
ADMIN_USERNAMES = {"shuify", "dochains"}


def is_admin(sender):
    try:
        username = sender.username
        if username and username.lower() in ADMIN_USERNAMES:
            return True
    except:
        pass
    return False


async def create_deal_group(event, pfp, admin_id):
    global deal_counter
    deal_num = deal_counter
    deal_counter += 1
    title = f"Deal #{deal_num} • @Secureble"

    try:
        result = await client(CreateChannelRequest(
            title=title,
            about="Always confirm that you are dealing with me and not with an impersonator!",
            megagroup=True
        ))

        chat = result.chats[0]

        # Admin entity
        try:
            admin = await client.get_input_entity(admin_id)
        except Exception:
            await event.reply("⚠️ Admin entity nahi mili. Pehle Shuify bot ko DM kare.")
            return None, None

        creator = await client.get_me()

        # ── Invite admin (Shuify) ────────────────────────────────────────
        await client(InviteToChannelRequest(chat, [admin]))

        await client(EditAdminRequest(
            channel=chat,
            user_id=admin,
            admin_rights=admin_rights_shuify,    # Shuify: anonymous OFF
            rank="Middleman"
        ))

        # ── Creator (Owner) ko sab rights ke saath tag karo ─────────────
        await client(EditAdminRequest(
            channel=chat,
            user_id=creator,
            admin_rights=admin_rights_owner,     # Owner: anonymous ON, sab ON
            rank="Manager"
        ))

        # Upload PFP
        file = await client.upload_file(pfp)
        await client(EditPhotoRequest(
            channel=chat,
            photo=InputChatUploadedPhoto(file)
        ))

        # Bot add
        try:
            bot_entity = await client.get_entity(BOT_USERNAME)
            await client(InviteToChannelRequest(chat, [bot_entity]))
            await client(EditAdminRequest(
                channel=chat,
                user_id=bot_entity,
                admin_rights=admin_rights_shuify,
                rank=BOT_TITLE
            ))
        except Exception as bot_err:
            await event.reply(f"⚠️ Bot add manually karo @Secureblebot\nError: {bot_err}")

        # Invite link
        invite = await client(ExportChatInviteRequest(chat))
        await event.reply(f"✅ Group Created – Deal {deal_num}\n\n{invite.link}")

        return chat.id, deal_num

    except Exception as e:
        await event.reply(f"❌ Error:\n{e}")
        return None, None


# ── /mm ──────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/mm"))
async def ziox_group(event):
    sender = await event.get_sender()
    if not is_admin(sender):
        return
    await create_deal_group(event, PFP1, CREATEGROUP_ADMIN)


# ── /close ────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/close"))
async def close_deal(event):
    sender = await event.get_sender()
    if not is_admin(sender):
        return
    msg = (
        "🤝 This deal is now closed with status: Successful.\n\n"
        "The group will be deleted automatically in 30 minutes."
    )
    sent = await event.reply(msg)
    await asyncio.sleep(1800)
    try:
        await client(DeleteChannelRequest(event.chat_id))
    except Exception:
        pass


# ── /clear ────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/clear"))
async def clear_chat(event):
    sender = await event.get_sender()
    if not is_admin(sender):
        return
    try:
        await client.delete_messages(event.chat_id, range(1, 999999))
        sent = await event.reply("✅ Chat history cleared for all members.")
        await asyncio.sleep(2)
        await client.delete_messages(event.chat_id, sent.id)
    except Exception as e:
        await event.reply(f"❌ Clear error: {e}")


# ── Auto-delete service messages ─────────────────────────────────────────
@client.on(events.NewMessage)
async def delete_service_messages(event):
    try:
        if isinstance(event.message.action, (
            MessageActionChatAddUser,
            MessageActionChatJoinedByLink,
            MessageActionChatEditPhoto,
            MessageActionChatEditTitle,
            MessageActionChatDeletePhoto
        )):
            await event.delete()
    except:
        pass


print("🔥 Auto MM Group Creator Running... (Deals start from 274)")

client.start()
client.run_until_disconnected()