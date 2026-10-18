
#include <stdio.h>
#include <string.h>
#include <stdlib.h>				/* getenv() */
#include <sys/stat.h>			/* mkdir() */
#include "hscores.h"

#ifdef _WIN32
#define MKDIR(dir) mkdir(dir)
#else
#define MKDIR(dir) mkdir(dir, S_IRWXU)
#endif

/* The folder for the high score file, with a trailing separator:
 * $XDG_DATA_HOME/nflood/, else ~/.local/share/nflood/ (%APPDATA%\nflood\
 * on Windows). Returns false when there is no such place. */
static bool score_folder(char* path, size_t size)
{
#ifdef _WIN32
	const char* appdata = getenv("APPDATA");
	if (appdata == NULL || appdata[0] == '\0')
		return false;
	snprintf(path, size, "%s\\" SCORE_DIR "\\", appdata);
#else
	const char* xdg  = getenv("XDG_DATA_HOME");
	const char* home = getenv("HOME");

	/* an empty or relative XDG_DATA_HOME counts as unset (XDG spec) */
	if (xdg != NULL && xdg[0] == '/')
		snprintf(path, size, "%s/" SCORE_DIR "/", xdg);
	else if (home != NULL && home[0] != '\0')
		snprintf(path, size, "%s/.local/share/" SCORE_DIR "/", home);
	else
		return false;
#endif
	return true;
}

/* Local function that creates a directory tree recurstively,
 * just like `mkdir -p` on UNIX-like systems.
 *
 * Doesn't check for errors though.
 * Based on this: http://stackoverflow.com/a/2336245/1094964
 */
void mkdir_p(const char* dir)
{
	char   tmp[4096];
	char*  p = NULL;
	size_t len;

	snprintf(tmp, sizeof(tmp), "%s", dir);
	len = strlen(tmp);

	if (tmp[len - 1] == '/')
		tmp[len - 1] = '\0';

	/* Traverse `dir` making all directories,
	 * temporarily replacing '/' by '\0' so mkdir()
	 * can work.
	 */
	for (p = tmp + 1; *p != '\0'; p++)
	{
		if (*p == '/' || *p == '\\')
		{
			char sep = *p;
			*p = '\0';
			MKDIR(tmp);
			*p = sep;
		}
	}
	MKDIR(tmp);
}

/** Opens default high score file, returning a FILE* handle to it.
 *  @return NULL if couldn't open the file.
 */
FILE* hscore_open(char* flags)
{
	char full_path[4096];

	if (!score_folder(full_path, sizeof(full_path) - strlen(SCORE_FILE)))
		return NULL;

	/* Making sure all directories exist first */
	mkdir_p(full_path);

	strcat(full_path, SCORE_FILE);

	return fopen(full_path, flags);
}

bool hscore_init()
{
	FILE* file = hscore_open("rb");

	/* First time creating the file */
	if (file == NULL)
	{
		hscore_clean();

		file = hscore_open("rb");

		/* really couldn't open file, we give up */
		if (file == NULL)
			return false;
	}

	fclose(file);
	return true;
}

void hscore_clean()
{
	FILE* file = hscore_open("wb");

	if (file != NULL)
	{
		int val = HIGH_SCORE_DEFAULT;

		fwrite(&val, sizeof(int), 1, file);
		fclose(file);
	}
}

bool hscore_store(int score)
{
	FILE* file = hscore_open("r+b");

	if (file == NULL)
		return false;

	fwrite(&score, sizeof(int), 1, file);
	fclose(file);
	return true;
}

int hscore_get()
{
	FILE* file = hscore_open("rb");

	if (file == NULL)
		return false;

	int hscore = HIGH_SCORE_DEFAULT;
	int items_read = fread(&hscore, sizeof(int), 1, file);
	fclose(file);

	/* badly formatted high score file - maybe erase it? */
	if (items_read != 1)
		return -1;

	return hscore;
}

