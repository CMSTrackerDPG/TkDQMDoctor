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
from certhelper.utilities.utilities import create_userprofile, update_userprofile

logger = get_configured_logger(loggername=__name__, filename="signals.log")


@receiver(post_save, sender=User)
def save_or_create_userprofile(sender, instance, created, raw, **kwargs):
    """
    Automatically creates a UserProfile when a new User is created and
    automatically saves the Users UserProfile when the save method is called.
    """
    if created:
        if not raw:  # Do not create UserProfile when using manage.py loaddata
            create_userprofile(instance)
        logger.info("New User {} has been created".format(instance))
    else:
        try:
            instance.userprofile.save()
            logger.info("UserProfile with id {} for User {} has been saved"
                        .format(instance.userprofile.id, instance))
        except UserProfile.DoesNotExist:
            logger.error("User {} does not have a UserProfile".format(instance))
            create_userprofile(instance)
        logger.info("User {} has been saved".format(instance))


@receiver(allauth.socialaccount.signals.social_account_added)
def update_newly_added_user(request, sociallogin, **kwargs):
    logger.info("Updating UserProfile of newly added Social Account {}"
                .format(sociallogin.user))
    update_userprofile(sociallogin.user)


@receiver(django.contrib.auth.signals.user_logged_in)
def update_users_userprofile_on_login(sender, user, request, **kwargs):
    update_userprofile(user)
    user.save()


@receiver(pre_save, sender=User)
def update_users_userprofile_on_save(sender, instance, **kwargs):
    if instance.pk:
        update_userprofile(instance)


@receiver(django.contrib.auth.signals.user_logged_in)
def log_user_logged_in(sender, user, request, **kwargs):
    logger.info("User {} has logged in".format(user))


@receiver(allauth.account.signals.user_logged_in)
def log_allauth_user_logged_in(request, user, **kwargs):
    logger.debug("User {} has logged in via allauth".format(user))


@receiver(django.contrib.auth.signals.user_logged_out)
def log_user_logged_out(sender, user, request, **kwargs):
    logger.info("User {} has logged out".format(user))


@receiver(allauth.socialaccount.signals.pre_social_login)
def log_pre_social_login(request, sociallogin, **kwargs):
    try:
        logger.debug("Pre social login for User {}".format(sociallogin.user))
    except (User.DoesNotExist, AttributeError):
        logger.debug("Pre social login for non-existing User")


@receiver(allauth.socialaccount.signals.social_account_added)
def log_social_account_added(request, sociallogin, **kwargs):
    try:
        logger.info("Social Account {} has been added for User {}"
                    .format(sociallogin.account, sociallogin.user))
    except (SocialAccount.DoesNotExist, User.DoesNotExist, AttributeError):
        logger.debug("Pre social login for non-existing User")


@receiver(allauth.socialaccount.signals.social_account_updated)
def log_social_account_updated(request, sociallogin, **kwargs):
    try:
        logger.debug("Social Account {} has been updated for User {}"
                     .format(sociallogin.account, sociallogin.user))
    except (SocialAccount.DoesNotExist, User.DoesNotExist, AttributeError):
        logger.error("Something unexpected happened")


@receiver(allauth.socialaccount.signals.social_account_removed)
def log_social_account_removed(request, socialaccount, **kwargs):
    try:
        logger.info("Social Account {} has been removed from User {}"
                    .format(socialaccount, socialaccount.user))
    except (User.DoesNotExist, AttributeError):
        logger.error("Something unexpected happened")


@receiver(django.contrib.auth.signals.user_login_failed)
def log_user_has_login_failed(sender, credentials, request, **kwargs):
    try:
        logger.warning(
            "User {} has failed to logged in".format(credentials.get("username")))
    except AttributeError:
        logger.error("Username attribute does not exist!")
