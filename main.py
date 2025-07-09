import os
import asyncio
import discord
from discord.ext import commands
import logging
from bot.utils.logger import setup_logger
from bot.commands.moderation import ModerationCommands
from bot.commands.general import GeneralCommands
from bot.commands.utility import UtilityCommands
from bot.commands.admin import AdminCommands
from bot.commands.fun import FunCommands
from keep_alive import keep_alive

# Bot yapılandırması
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Bot prefix ve setup
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# Logger setup
logger = setup_logger()

@bot.event
async def on_ready():
    """Bot hazır olduğunda çalışır"""
    logger.info(f'{bot.user} olarak giriş yapıldı!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Sunucu sayısı: {len(bot.guilds)}')
    
    # Bot durumunu ayarla
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="sunucuyu | /help"
        )
    )
    
    # Slash komutları senkronize et
    try:
        synced = await bot.tree.sync()
        logger.info(f'{len(synced)} slash komutu senkronize edildi')
    except Exception as e:
        logger.error(f'Slash komutları senkronize edilirken hata: {e}')

@bot.event
async def on_command_error(ctx, error):
    """Komut hatalarını yönetir"""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Hata",
            description="Bu komut bulunamadı. `/help` komutu ile mevcut komutları görebilirsiniz.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Yetkisiz",
            description="Bu komutu kullanmak için gerekli yetkileriniz yok.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Eksik Parametre",
            description=f"Gerekli parametre eksik: `{error.param.name}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Hatalı Parametre",
            description="Geçersiz parametre girdiniz.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    else:
        logger.error(f'Beklenmeyen hata: {error}')
        embed = discord.Embed(
            title="❌ Beklenmeyen Hata",
            description="Bir hata oluştu. Lütfen tekrar deneyiniz.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Slash komut hatalarını yönetir"""
    if isinstance(error, discord.app_commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Yetkisiz",
            description="Bu komutu kullanmak için gerekli yetkileriniz yok.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    elif isinstance(error, discord.app_commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Bekleme Süresi",
            description=f"Bu komutu tekrar kullanmak için {error.retry_after:.1f} saniye bekleyiniz.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    else:
        logger.error(f'Slash komut hatası: {error}')
        embed = discord.Embed(
            title="❌ Beklenmeyen Hata",
            description="Bir hata oluştu. Lütfen tekrar deneyiniz.",
            color=discord.Color.red()
        )
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)

@bot.event
async def on_guild_join(guild):
    """Bot sunucuya katıldığında çalışır"""
    logger.info(f'Yeni sunucuya katıldı: {guild.name} (ID: {guild.id})')

@bot.event
async def on_guild_remove(guild):
    """Bot sunucudan ayrıldığında çalışır"""
    logger.info(f'Sunucudan ayrıldı: {guild.name} (ID: {guild.id})')

async def main():
    """Ana fonksiyon"""
    # Komut sınıflarını yükle
    await bot.add_cog(ModerationCommands(bot))
    await bot.add_cog(GeneralCommands(bot))
    await bot.add_cog(UtilityCommands(bot))
    await bot.add_cog(AdminCommands(bot))
    await bot.add_cog(FunCommands(bot))
    
    # Bot token'ını al
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('DISCORD_TOKEN environment variable bulunamadı!')
        return
    
    # Keep alive servisini başlat
    keep_alive()
    
    # Botu başlat
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info('Bot kapatılıyor...')
        await bot.close()
    except Exception as e:
        logger.error(f'Bot başlatılırken hata: {e}')

if __name__ == "__main__":
    asyncio.run(main())
