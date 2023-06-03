# Gentoo Linux image with 2 week old Portage source tree
FROM gentoo/stage3

# Sync Portage source tree
RUN emerge --sync

# Install git
RUN emerge --quiet --update --newuse dev-vcs/git

# Remove existing repository
RUN rm -rf /var/db/repos/gentoo

# Clone the Gentoo ebuild repository using git
RUN mkdir /var/db/repos/gentoo
RUN git clone --depth 1000 https://github.com/gentoo-mirror/gentoo.git /var/db/repos/gentoo

# Get the commit hash of the state of the repo two weeks ago
# Then, reset the repository to that state
RUN cd /var/db/repos/gentoo && pwd && git checkout $(git rev-list -n 1 --before="1 week ago" stable)

# Replace rsync with git in repos.conf
RUN mkdir '/etc/portage/repos.conf'
RUN echo -e "[DEFAULT]\n\
main-repo = gentoo\n\
\n\
[gentoo]\n\
location = /var/db/repos/gentoo\n\
sync-type = git\n\
sync-uri = https://github.com/gentoo-mirror/gentoo.git" > /etc/portage/repos.conf/gentoo.conf

