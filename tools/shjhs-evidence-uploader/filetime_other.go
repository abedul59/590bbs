//go:build !windows

package main

import "time"

func platformCreationTime(_ string) (time.Time, bool) {
	return time.Time{}, false
}
