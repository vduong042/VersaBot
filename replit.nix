{ pkgs }: {
  deps = [
    pkgs.wget
    pkgs.ffmpeg_6-full
    pkgs.libopus.out
  ];
  env = {
    IMAGEIO_FFMPEG_EXE = "${pkgs.ffmpeg_6-full}/bin/ffmpeg";
    OPUS_PATH = "${pkgs.libopus.out}/lib";
  };
}