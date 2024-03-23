{ pkgs }: {
  deps = [
    pkgs.libsodium
    pkgs.wget
    pkgs.ffmpeg_6-full
    pkgs.libopus.out
    pkgs.python311Packages.pynacl
  ];
  env = {
    IMAGEIO_FFMPEG_EXE = "${pkgs.ffmpeg_6-full}/bin/ffmpeg";
    OPUS_PATH = "${pkgs.libopus.out}/lib";
  };
}