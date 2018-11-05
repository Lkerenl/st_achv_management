CREATE TABLE "course" (
  "id" INTEGER CONSTRAINT "pk_course" PRIMARY KEY,
  "cno" TEXT NOT NULL,
  "cname" TEXT NOT NULL,
  "cclass" TEXT NOT NULL,
  "ctype" TEXT NOT NULL,
  "ccredits" INTEGER,
  "ctime" TEXT NOT NULL
);

CREATE TABLE "management" (
  "id" INTEGER CONSTRAINT "pk_management" PRIMARY KEY,
  "no" TEXT NOT NULL,
  "password" TEXT NOT NULL
);

CREATE TABLE "score" (
  "id" INTEGER CONSTRAINT "pk_score" PRIMARY KEY,
  "score" DOUBLE PRECISION
);

CREATE TABLE "course_scores" (
  "course" INTEGER NOT NULL,
  "score" INTEGER NOT NULL,
  CONSTRAINT "pk_course_scores" PRIMARY KEY ("course", "score")
);

CREATE INDEX "idx_course_scores" ON "course_scores" ("score");

ALTER TABLE "course_scores" ADD CONSTRAINT "fk_course_scores__course" FOREIGN KEY ("course") REFERENCES "course" ("id");

ALTER TABLE "course_scores" ADD CONSTRAINT "fk_course_scores__score" FOREIGN KEY ("score") REFERENCES "score" ("id");

CREATE TABLE "student" (
  "id" INTEGER CONSTRAINT "pk_student" PRIMARY KEY,
  "no" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "password" TEXT NOT NULL,
  "ssex" TEXT NOT NULL,
  "sclass" TEXT NOT NULL,
  "sgrade" TEXT NOT NULL
);

CREATE TABLE "score_students" (
  "student" INTEGER NOT NULL,
  "score" INTEGER NOT NULL,
  CONSTRAINT "pk_score_students" PRIMARY KEY ("student", "score")
);

CREATE INDEX "idx_score_students" ON "score_students" ("score");

ALTER TABLE "score_students" ADD CONSTRAINT "fk_score_students__score" FOREIGN KEY ("score") REFERENCES "score" ("id");

ALTER TABLE "score_students" ADD CONSTRAINT "fk_score_students__student" FOREIGN KEY ("student") REFERENCES "student" ("id");

CREATE TABLE "teacher" (
  "id" INTEGER CONSTRAINT "pk_teacher" PRIMARY KEY,
  "no" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "password" TEXT NOT NULL,
  "tprofession" TEXT NOT NULL
);

CREATE TABLE "course_teachers" (
  "course" INTEGER NOT NULL,
  "teacher" INTEGER NOT NULL,
  CONSTRAINT "pk_course_teachers" PRIMARY KEY ("course", "teacher")
);

CREATE INDEX "idx_course_teachers" ON "course_teachers" ("teacher");

ALTER TABLE "course_teachers" ADD CONSTRAINT "fk_course_teachers__course" FOREIGN KEY ("course") REFERENCES "course" ("id");

ALTER TABLE "course_teachers" ADD CONSTRAINT "fk_course_teachers__teacher" FOREIGN KEY ("teacher") REFERENCES "teacher" ("id")