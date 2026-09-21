CREATE TABLE `chunks` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`document_id` text NOT NULL,
	`ordinal` integer NOT NULL,
	`page` integer,
	`section` text NOT NULL,
	`text` text NOT NULL,
	`vector` text NOT NULL,
	FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `chunks_owner_document` ON `chunks` (`owner`,`document_id`);--> statement-breakpoint
CREATE TABLE `documents` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`title` text NOT NULL,
	`filename` text NOT NULL,
	`mime` text NOT NULL,
	`sha` text NOT NULL,
	`storage_key` text NOT NULL,
	`status` text NOT NULL,
	`chunks` integer DEFAULT 0 NOT NULL,
	`characters` integer NOT NULL,
	`embedding_model` text NOT NULL,
	`created_at` text NOT NULL,
	`extraction` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `documents_owner_sha` ON `documents` (`owner`,`sha`);--> statement-breakpoint
CREATE INDEX `documents_owner` ON `documents` (`owner`);--> statement-breakpoint
CREATE TABLE `edges` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`source` text NOT NULL,
	`target` text NOT NULL,
	`relation` text NOT NULL,
	`quote` text NOT NULL,
	`chunk_id` text NOT NULL,
	FOREIGN KEY (`source`) REFERENCES `entities`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`target`) REFERENCES `entities`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`chunk_id`) REFERENCES `chunks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `edges_owner_source` ON `edges` (`owner`,`source`);--> statement-breakpoint
CREATE INDEX `edges_owner_target` ON `edges` (`owner`,`target`);--> statement-breakpoint
CREATE TABLE `entities` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`label` text NOT NULL,
	`kind` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `entities_owner` ON `entities` (`owner`);--> statement-breakpoint
CREATE TABLE `limits` (
	`id` text PRIMARY KEY NOT NULL,
	`count` integer NOT NULL,
	`expires` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `mentions` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`entity_id` text NOT NULL,
	`chunk_id` text NOT NULL,
	FOREIGN KEY (`entity_id`) REFERENCES `entities`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`chunk_id`) REFERENCES `chunks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `mentions_owner_entity` ON `mentions` (`owner`,`entity_id`);--> statement-breakpoint
CREATE TABLE `queries` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`question` text NOT NULL,
	`response` text NOT NULL,
	`mode` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `queries_owner` ON `queries` (`owner`);