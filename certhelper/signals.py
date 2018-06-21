import allauth
import django
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import social_account_updated
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from certhelper.models import UserProfile
from certhelper.utilities.logger import get_configured_logger

logger = get_configured_logger(loggername=__name__, filename="signals.log")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Called when a new User has been created
    """
    if created:
        logger.info("UserProfile has been created for {}".format(instance))
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Called when an existing User has been updated
    """
    try:
        instance.userprofile.save()
        logger.debug("UserProfile has been saved for {}".format(instance))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(django.contrib.auth.signals.user_logged_in)
def log_user_logged_in(sender, user, request, **kwargs):
    try:
        logger.info("User {} has logged in".format(user))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(django.contrib.auth.signals.user_logged_out)
def log_user_logged_out(sender, user, request, **kwargs):
    try:
        logger.info("User {} has logged out".format(user))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(django.contrib.auth.signals.user_login_failed)
def log_user_has_login_failed(sender, credentials, request, **kwargs):
    try:
        logger.warning("User {} has failed to logged in".format(credentials.get("username")))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(allauth.account.signals.user_logged_in)
def log_allauth_user_logged_in(request, user, **kwargs):
    try:
        logger.debug("User {} has logged in via allauth".format(user))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(allauth.socialaccount.signals.pre_social_login)
def log_pre_social_login(request, sociallogin, **kwargs):
    try:
        logger.debug("Pre social login for User {}".format(sociallogin.user))
    except User.DoesNotExist:
        logger.debug("Pre social login for non-existing User")
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(allauth.socialaccount.signals.social_account_added)
def log_social_account_added(request, sociallogin, **kwargs):
    try:
        logger.info("Social Account {} has been added for User {}".format(sociallogin.account, sociallogin.user))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(allauth.socialaccount.signals.social_account_updated)
def log_social_account_updated(request, sociallogin, **kwargs):
    try:
        logger.debug("Social Account {} has been updated for User {}".format(sociallogin.account, sociallogin.user))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(allauth.socialaccount.signals.social_account_removed)
def log_social_account_removed(request, socialaccount, **kwargs):
    try:
        logger.info("Social Account {} has been removed from User {}".format(socialaccount, socialaccount.user))
    except Exception as e:
        logger.error("Failed to log")
        logger.exception(e)


@receiver(allauth.socialaccount.signals.social_account_added)
@receiver(allauth.account.signals.user_logged_in)
def update_user_privilege_by_e_groups(request, user, **kwargs):
    try:
        socialaccount = SocialAccount.objects.get(user=user)
    except SocialAccount.DoesNotExist:
        logger.warning("No SocialAccount exists for User {}".format(user))
        return

    try:
        userprofile = socialaccount.user.userprofile
    except AttributeError:
        try:
            logger.info("User {} has no UserProfile!".format(socialaccount.user))
            UserProfile.objects.create(user=socialaccount.user)
            logger.info("UserProfile was therefore created subsequently for {}".format(socialaccount.user))
            userprofile = socialaccount.user.userprofile
        except Exception as e:
            logger.critical("Unable to create UserProfile")
            logger.exception(e)
            return

    try:
        userprofile.extra_data.update(socialaccount.extra_data)
        logger.debug("SocialLogins extra_data {}".format(socialaccount.extra_data))
        userprofile.upgrade_user_privilege()
        userprofile.user.save()
        logger.debug("Extra data have been updated for {}".format(socialaccount.user))
    except Exception as e:
        logger.critical("Unable to upgrade User privilege")
        logger.exception(e)
        return
