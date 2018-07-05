import allauth
import django
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import social_account_updated
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from certhelper.models import UserProfile
from certhelper.utilities.logger import get_configured_logger

logger = get_configured_logger(loggername=__name__, filename="signals.log")


@receiver(post_save, sender=UserProfile)
def userprofile_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info("New UserProfile with id {} for User {} has been created".format(instance.id, instance.user))
    else:
        logger.info("UserProfile with id {} for User {} has been saved".format(instance.id, instance.user))


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info("New User {} with id {} has been created".format(instance, instance.id))
    else:
        logger.info("User {} with id {} has been saved".format(instance, instance.id))


@receiver(django.contrib.auth.signals.user_logged_in)
def log_user_logged_in(sender, user, request, **kwargs):
    logger.info("User {} has logged in".format(user))


@receiver(django.contrib.auth.signals.user_logged_out)
def log_user_logged_out(sender, user, request, **kwargs):
    logger.info("User {} has logged out".format(user))


@receiver(django.contrib.auth.signals.user_login_failed)
def log_user_has_login_failed(sender, credentials, request, **kwargs):
    try:
        logger.warning("User {} has failed to logged in".format(credentials.get("username")))
    except AttributeError:
        logger.error("Username attribute does not exist!")


@receiver(allauth.account.signals.user_logged_in)
def log_allauth_user_logged_in(request, user, **kwargs):
    logger.debug("User {} has logged in via allauth".format(user))


@receiver(allauth.socialaccount.signals.pre_social_login)
def log_pre_social_login(request, sociallogin, **kwargs):
    try:
        logger.debug("Pre social login for User {}".format(sociallogin.user))
    except (User.DoesNotExist, AttributeError):
        logger.debug("Pre social login for non-existing User")


@receiver(allauth.socialaccount.signals.social_account_added)
def log_social_account_added(request, sociallogin, **kwargs):
    try:
        logger.info("Social Account {} has been added for User {}".format(sociallogin.account, sociallogin.user))
    except (SocialAccount.DoesNotExist, User.DoesNotExist, AttributeError):
        logger.debug("Pre social login for non-existing User")


@receiver(allauth.socialaccount.signals.social_account_updated)
def log_social_account_updated(request, sociallogin, **kwargs):
    try:
        logger.debug("Social Account {} has been updated for User {}".format(sociallogin.account, sociallogin.user))
    except (SocialAccount.DoesNotExist, User.DoesNotExist, AttributeError):
        logger.error("Something unexpected happened")


@receiver(allauth.socialaccount.signals.social_account_removed)
def log_social_account_removed(request, socialaccount, **kwargs):
    try:
        logger.info("Social Account {} has been removed from User {}".format(socialaccount, socialaccount.user))
    except (User.DoesNotExist, AttributeError):
        logger.error("Something unexpected happened")


@receiver(allauth.socialaccount.signals.social_account_added)
def update_newly_added_user_privilege_by_e_groups(request, sociallogin, **kwargs):
    try:
        update_user_privilege_by_e_groups(request, sociallogin.user, **kwargs)
    except (User.DoesNotExist, AttributeError):
        logger.error("Something unexpected happened")


@receiver(allauth.account.signals.user_logged_in)
def update_user_privilege_by_e_groups(request, user, **kwargs):
    try:
        socialaccount = SocialAccount.objects.get(user=user)
    except SocialAccount.DoesNotExist:
        logger.warning("No SocialAccount exists for User {}".format(user))
        return

    try:
        userprofile = socialaccount.user.userprofile
    except UserProfile.DoesNotExist:
        try:
            logger.info("No UserProfile exists for User {}!".format(socialaccount.user))
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
