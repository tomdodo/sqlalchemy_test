create table Company (
	`id` integer primary key,
	`name` varchar(200)
);

create table User (
	`id` integer primary key,
	`name` varchar(200),
	`company_id` integer,
	foreign key (`company_id`) references `Company` (`id`) on delete cascade
);

create table Email (
	`id` integer primary key,
	`type` enum('home', 'work', 'other') not null,
	`email` varchar(100),
	`user_id` integer,
	foreign key (user_id) references `User`(`id`) on delete cascade
);

create table PhoneNumber (
	`id` integer primary key,
	`type` enum('home', 'work', 'other') not null,
	`phone_number` varchar(50),
	`user_id` integer,
	foreign key (`user_id`) references `User`(`id`) on delete cascade
);
