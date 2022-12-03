FROM centos:7.9.2009

RUN yum -y update && yum install -y openssh-server

RUN mkdir /var/run/sshd

RUN ssh-keygen -A

RUN echo 'root:password' | chpasswd

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

EXPOSE 2222

CMD ["/usr/sbin/sshd", "-D"]
