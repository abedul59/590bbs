//go:build windows

package main

import (
	"syscall"
	"time"
	"unsafe"
)

func platformCreationTime(path string) (time.Time, bool) {
	pointer, err := syscall.UTF16PtrFromString(path)
	if err != nil {
		return time.Time{}, false
	}
	var data syscall.Win32FileAttributeData
	if err := syscall.GetFileAttributesEx(pointer, syscall.GetFileExInfoStandard, (*byte)(unsafe.Pointer(&data))); err != nil {
		return time.Time{}, false
	}
	return time.Unix(0, data.CreationTime.Nanoseconds()), true
}
