# 1. Ansible playbook

Данные пользователя:
- Username: cloudru
- Password: cloudpass
- user ID: 200
- shell: bash
- group: web

## Создаем yml файл
-- ansible/user.yml

## Создадим пользователя cloudru и SSH для пользователя 
```
- name: create user cloudru
      user:
        name: cloudru
        uid: 200
        shell: /bin/bash
        groups: web
        append: yes
        generate_ssh_key: yes
        ssh_key_file: .ssh/id_rsa
```
- generate_ssh_key - эта опция используется для генерации ключа SSH для пользователя, в этом случае ключ SSH будет сгенерирован для пользователя cloudru. Этот вариант не будет перезаписывать существующий ключ SSH, если он не используется с Force=yes.
- ssh_key_file - место, где храниться SSH


## Создадим файл в каталоге sudoers.d, чтобы cloudru мог полностью выполнять свои функции в качестве пользователя root, не запрашивая у него ввода пароля.
```
- name: create /etc/sudoers.d/cloudru file
      file:
        path: /etc/sudoers.d/cloudru
        state: touch

    - name: configure a pass-wordless authentication & execution for cloudru
      lineinfile:
        path: /etc/sudoers.d/cloudru
        line: "cloudru ALL=(ALL) NOPASSWD: ALL"
        state: present
```
## Вход по SSH
В дальнейшем вход в управляемый хост с управляющего узла через SSH должен осуществляться без пароля.
Это означает, что нам нужно установить ключ SSH от управляющего узла к управляемому узлу. Это можно сделать с помощью модуля authorized_key.
```
- name: install the SSH public key on managed host for cloudru
      authorized_key:
        user: cloudru
        state: present
        key: "{{ lookup('file', '/home/marakya/.ssh/id_rsa.pub') }}"
```  
- authorized_key: Этот модуль будет использоваться для установки SSH-ключа.
- user: Этот параметр означает, что для пользователя cloudru будет установлен файл SSH-ключа
- state: Этот параметр предназначен для указания того, должен ли ключ быть в файле или нет. Присутствует значение по умолчанию.
- key: В этом параметре будет указан SSH-ключ.

## Пароль
Также необходимо утсановить пароль для пользователя cloudru. На машинах Linux пароли должны быть зашифрованы и анализироваться с использованием переменных.
Тогда начальную часть кода перепишем:
```
- name: create user cloudru
  hosts: webservers
  vars:
     - passwrd: cloudpass
  tasks:
    - name: create user cloudru
      user:
        name: cloudru
        uid: 200
        shell: /bin/bash
        groups: web
        append: yes
        generate_ssh_key: yes
        ssh_key_file: .ssh/id_rsa
        password: "{{ passwrd | password_hash('sha512') }}"
```
Итоговый код user.yml:
```
- name: create user cloudru
  hosts: webservers
  vars:
     - passwrd: cloudpass
  tasks:
    - name: create user cloudru
      user:
        name: cloudru
        uid: 200
        shell: /bin/bash
        groups: web
        append: yes
        generate_ssh_key: yes
        ssh_key_file: .ssh/id_rsa
        password: "{{ passwrd | password_hash('sha512') }}"

    - name: create /etc/sudoers.d/cloudru file
      file:
        path: /etc/sudoers.d/cloudru
        state: touch

    - name: configure a pass-wordless authentication & execution for cloudru
      lineinfile:
        path: /etc/sudoers.d/cloudru
        line: "cloudru ALL=(ALL) NOPASSWD: ALL"
        state: present
      
    - name: install the SSH public key on managed host for cloudru
      authorized_key:
        user: cloudru
        state: present
        key: "{{ lookup('file', '/home/marakya/.ssh/id_rsa.pub') }}"

```

      
  