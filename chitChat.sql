DROP DATABASE IF EXISTS chitchat;
CREATE DATABASE chitchat;
\c chitchat;
CREATE EXTENSION pgcrypto;
--
-- Table structure for table messages
--
DROP TABLE IF EXISTS messages;
CREATE TABLE IF NOT EXISTS messages (
  id serial NOT NULL,
  userid varchar(70) NOT NULL,
  message varchar(200) NOT NULL,
  room varchar(25),
  PRIMARY KEY (id)
) ;

INSERT INTO messages (userid, message, room) VALUES
('TheWolfman', 'Watchout for the Wolfman', NULL),
('Hillary', 'Is Hillary running?', 'B'),
('Gusty', 'Gusty programmed some of this code',NULL);

--
-- Table structure for table users
--

DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
  id serial NOT NULL,
  username varchar(12) NOT NULL,
  password varchar(126) NOT NULL,
  restrictions varchar(126) NOT NULL,
  PRIMARY KEY (id)
)  ;

---  INSERT INTO users (username,password,restrictions) VALUES ('raz',crypt('p00d13',gen_salt('bf')),'none')
INSERT INTO users (username, password, restrictions) VALUES
('raz', crypt('p00d13',gen_salt('bf')), 'none'),
('ann', crypt('changeme',gen_salt('bf')), 'none'),
('gusty', crypt('gusty',gen_salt('bf')), 'none'),
('jerrianne', crypt('jerrianne',gen_salt('bf')), 'none'),
('jeremy', crypt('jeremy',gen_salt('bf')), 'none'),
('brandalee', crypt('brandalee',gen_salt('bf')), 'none'),
('zachary', crypt('zachary',gen_salt('bf')), 'none'),
('emily', crypt('emily',gen_salt('bf')), 'none'),
('lee', crypt('lee',gen_salt('bf')), 'none'),
('ron', crypt('ron',gen_salt('bf')), 'none'),
('chris', crypt('chris',gen_salt('bf')), 'none'),
('thomas', crypt('thomas',gen_salt('bf')), 'none'),
('shehan', crypt('shehan',gen_salt('bf')), 'none'),
('james', crypt('james',gen_salt('bf')), 'none'),
('shana', crypt('shana',gen_salt('bf')), 'none'),
('tyler', crypt('tyler',gen_salt('bf')), 'none'),
('taka', crypt('taka',gen_salt('bf')), 'none'),
('campbell', crypt('campbell',gen_salt('bf')), 'none'),
('sepehr', crypt('sepehr',gen_salt('bf')), 'none'),
('zach', crypt('zach',gen_salt('bf')), 'none'),
('eric', crypt('eric',gen_salt('bf')), 'none'),
('lazy', crypt('qwerty',gen_salt('bf')), 'none');



